from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.urls import reverse_lazy

import git
import tempfile
import shutil
import os
import datetime

from .models import Components, Files, Parameters

from lxml.etree import XMLParser, XSLT
import xml.etree.ElementTree as ET
from xmlschema import XMLSchema10, XMLSchemaValidationError
from django.template import engines

from management_web_app.settings import GIT_URL


@login_required(login_url=reverse_lazy("auth:login"))
def index(request):
    return render(request, "index.html", {"user": request.user})


@login_required(login_url=reverse_lazy("auth:login"))
def components(request):
    components: dict[str, list[str]] = {}
    for c in Components.objects.all():
        if c.name not in components.keys():
            components[c.name] = []
        for f in Files.objects.filter(component_id=c.id):
            components[c.name].append(f)

    return render(request, "components.html", {"components": components})


@login_required(login_url=reverse_lazy("auth:login"))
def editparams(request):
    parser = XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    xml_file = ""
    msg = ""
    elem = ""
    file: Files = None

    if request.method == "POST":
        # get session parameters (file and xml_file)
        file_id = request.session.get("file_id")
        xml_file = request.session.get("xml_file")

        file = Files.objects.get(id=file_id)  # get file entry from db

        root = ET.fromstring(xml_file, parser=parser)
        # change values
        for item in request.POST.items():
            if root.find(item[0][1:]) is not None:
                root.find(item[0][1:]).text = item[1]

        temp = tempfile.mkdtemp()  # create temp folder
        repo = git.Repo.clone_from(GIT_URL, temp)  # clone git repo

        # load xsd from repo
        xsd_gitslug = file.xsd_gitslug
        xsd_str = open(os.path.join(temp, xsd_gitslug)).read()
        xsd = XMLSchema10(ET.fromstring(xsd_str, parser=parser))

        if xsd.is_valid(root):  # validate
            # load xslt from repo
            xslt_gitslug = file.xslt_gitslug
            xslt_str = open(os.path.join(temp, xslt_gitslug)).read()
            xslt_root = ET.fromstring(xslt_str, parser=parser)

            # transform
            transform = XSLT(xslt_root)
            result = transform(root)

            # override
            gitslug = file.gitslug
            with open(os.path.join(temp, gitslug), "w") as f:
                f.write(str(result).replace('<?xml version="1.0"?>', ""))

            repo.index.add([gitslug])

            # commit and push changes if exists and save to db
            if repo.is_dirty(untracked_files=True):
                print("Changes detected.")
                repo.index.commit(
                    "Change with configuration interface in "
                    + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                )
                repo.remotes.origin.push()
                params = Parameters.objects.filter(file_id=file_id)
                for item in request.POST.items():
                    par = params.filter(absxpath=item[0]).first()
                    if par is not None:
                        par.value = item[1]
                        par.save()
                msg = "Значения параметров успешно изменены и зафиксированы в git!"
            else:
                msg = "Изменений не было!"

            xml_file = '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(
                root, file.fencoding
            ).decode(file.fencoding)
            shutil.rmtree(temp)  # delete temp folder
        else:
            try:
                xsd.validate(root)
            except XMLSchemaValidationError as e:
                elem = e.path.removeprefix(f"/{e.root.tag}")
                if elem.find("[") > 0 and elem.rfind("]") > 0:
                    attr = f"""[@n="{elem[elem.find('[')+1:elem.rfind(']')]}"]"""
                    elem = elem[: elem.find("[")] + attr + elem[elem.rfind("]") + 1:]
                msg = f"Ошибка валидации: параметр {elem}!"
            except Exception:
                msg = "Неизвестная ошибка"
    else:
        file_id = request.GET["file_id"]  # get url param
        request.session["file_id"] = file_id  # store file_id as session param

        params = Parameters.objects.filter(file_id=file_id).order_by(
            "id"
        )  # get file parameters entry from db

        # build xml file
        root = ET.Element("xml_repr")
        for param in params:
            root = param.add_to_ET(root)

        file = Files.objects.get(id=file_id)  # get file entry from db

        xml_file = '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(
            root, file.fencoding
        ).decode(file.fencoding)
        request.session["xml_file"] = xml_file  # store xml_file as session param

    # xml -> html
    xslt = loader.get_template("stylesheet_universal.xsl").template.source.encode(
        "utf-8"
    )  # common xslt
    xslt_root = ET.fromstring(xslt, parser=parser)
    xml_doc = ET.fromstring(xml_file, parser=parser)
    transform = XSLT(xslt_root)
    result = transform(xml_doc)

    # intermediate template
    template = engines["django"].from_string(str(result))
    half_rendered_remplate = template.render({"el": elem, "reason": "Ошибка тут!"})

    return render(
        request,
        "result.html",
        {"result": half_rendered_remplate, "errors": msg, "file": file.filename},
    )
