from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .models import Components, Files, Parameters
from .forms import CustomForm
from .classes import RepoManager
from . import functions as fn

from django.template import engines

from core.settings import GIT_URL


@login_required(login_url=reverse_lazy("auth:login"))
def index(request):
    return render(request, "config_management/index.html", {"user": request.user})


@login_required(login_url=reverse_lazy("auth:login"))
def components(request):
    components = Components.objects.all().order_by("id")
    files = Files.objects.all()
    cnts = []

    for c in components:
        cnts.append(files.filter(component_id=c.id).count())

    return render(request, "config_management/components.html", {"components": zip(cnts, components)})


@login_required(login_url=reverse_lazy("auth:login"))
def configs(request):
    component_id = ""
    if request.GET:
        component_id = request.GET["component_id"]

    files = Files.objects.filter(component_id=component_id).order_by("id")
    params = Parameters.objects.all()
    cnts = []

    for f in files:
        cnts.append(params.filter(file_id=f.id).count())  

    cur_component = Components.objects.get(id=component_id)

    return render(request, "config_management/configs.html", {"files": zip(cnts, files), "cur_component": cur_component})


@login_required(login_url=reverse_lazy("auth:login"))
def editparams(request):
    xml_file = ""
    msg = ""
    error_element = ""
    file: Files = None
    custom = CustomForm()

    if request.method == "POST":
        # get session parameters (file and xml_file)
        file_id = request.session.get("file_id")
        file = Files.objects.get(id=file_id)  

        xml_file = request.session.get("xml_file")
        root = fn.get_et_from_xml_str(xml_file)
        
        # change values
        for item in request.POST.items():
            if root.find(item[0][1:]) is not None:
                root.find(item[0][1:]).text = item[1]

        # clone repo or use already cloned
        repo: RepoManager = None
        if request.session.get("repo_path"):
            repo = RepoManager(GIT_URL, request.session.get("repo_path"))
        else: 
            repo = RepoManager(GIT_URL)
            request.session["repo_path"] = repo.temp

        # load xsd from repo
        xsd_str = repo.get_file_as_str(file.xsd_gitslug)

        # get xsd
        xsd = fn.get_xml_schema(xsd_str)

        # validate
        error_element = fn.validate_and_get_error(xsd, root) 

        if error_element is None:  # if no errors
            # load xslt from repo
            xslt_str = repo.get_file_as_str(file.xslt_gitslug)

            # transform
            result = fn.xslt_transform(xslt_str, root)

            # override
            repo.override_file(file.gitslug, str(result).replace('<?xml version="1.0"?>', ""))

            # commit and push changes if exists and save to db
            if repo.commit_changes():
                file.save_changes(request.POST.items())
                msg = "Parameter values successfully changed and committed to git!"
            else:
                msg = "No changes to save!"

            # preparying xml to transform
            xml_file = fn.get_xml_str_from_et(root, file.fencoding)
        else:
            msg = f"Validation error: parameter {error_element}!"
    else:
        file_id = request.GET["file_id"]  # get url param
        request.session["file_id"] = file_id  # store file_id as session param

        file = Files.objects.get(id=file_id)  # get file entry from db

        root = file.get_ET() # get ET of config file

        xml_file = fn.get_xml_str_from_et(root, file.fencoding) # build xml from ET
        request.session["xml_file"] = xml_file  # store xml_file as session param

    # xml -> html
    xslt_str = open("./apps/templates/config_management/stylesheet_universal.xsl").read().encode(file.fencoding) # common xslt
    root = fn.get_et_from_xml_str(xml_file)
    result = fn.xslt_transform(xslt_str, root)

    xpath_value = file.get_xpath_value_dict() # get xpath - value dictionary

    # intermediate template
    template = engines["django"].from_string(str(result))
    half_rendered_remplate = template.render(
        {
            "el": error_element,
            "reason": "Error here!",
            "params": xpath_value,
            "custom": custom
        }
    )

    cur_component = file.component

    return render(
        request,
        "config_management/editparams.html",
        {
            "result": half_rendered_remplate,
            "errors": msg,
            "file": file.filename,
            "cur_component": cur_component,
            "cur_config": file
        },
    )
