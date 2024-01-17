from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .models import Components, Files, Parameters
from .forms import CustomForm
from .classes import RepoManager
from . import functions as fn

from django.template import engines

from core.settings import GIT_URL
from django.views.generic import ListView


import xmltodict, json
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count

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
        root = fn.get_et_from_xml_str(xml_file) # to output
        root_with_true_custom = fn.get_et_from_xml_str(xml_file) # to change in git
        
        keys = [q["absxpath"] for q in file.parameters_set.values("absxpath")]

        # change values
        for key in keys:
            if key in request.POST.keys():
                if key.split('/')[-1] == "custom":
                    new_elem = fn.get_et_from_xml_str(xmltodict.unparse(json.loads('{"custom": ' + request.POST[key] + '}')))
                    elem = root_with_true_custom.find(key[1:])
                    elem.clear()
                    for item in new_elem:
                        elem.append(item)
                    #print(new_elem, "\n", fn.get_xml_str_from_et(root_with_true_custom))
                    root.find(key[1:]).text = request.POST[key]
                else:
                    root.find(key[1:]).text = request.POST[key]
                    root_with_true_custom.find(key[1:]).text = request.POST[key]
            else:
                root.find(key[1:]).text = "false"
                root_with_true_custom.find(key[1:]).text = "false"


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
        error_element = fn.validate_and_get_error(xsd, root_with_true_custom) 

        if error_element is None:  # if no errors
            # load xslt from repo
            xslt_str = repo.get_file_as_str(file.xslt_gitslug)

            # transform
            result = fn.xslt_transform(xslt_str, root_with_true_custom)

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

    query = file.parameters_set.all()

    for par in query:
        root.find(par.absxpath[1:]).set("type", par.input_type)

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


@login_required(login_url=reverse_lazy("auth:login"))
def configuration(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    n_pages = 5
    if is_ajax:
        if request.method == 'POST':
            ajax_type = request.POST.get('type', None)
            page_n = 1
            match ajax_type:
                case "set_scope":
                    component_id = request.POST.get('component_id', None)
                    request.session["filter_scope"] = component_id

                case "reset_scope":
                    request.session["filter_scope"] = None

                case "page_select":
                    page_n = request.POST.get('page_n', 1)

                case "text_search":
                    request.session["search_str"] = request.POST.get('search_str', None)

                case "reset_text_search":
                    request.session["search_str"] = None

                case "change_param":
                    new_value = request.POST.get('value', None)
                    param_id = request.POST.get('param_id', None)
                    param = Parameters.objects.get(id=param_id)
                    old_value = param.value

                    is_valid = fn.validate_parameter(request, param, new_value)

                    if "changes_dict" not in request.session.keys() or not request.session["changes_dict"]:
                        request.session["changes_dict"] = {}
                    
                    request.session["changes_dict"][param_id] = (new_value, old_value, is_valid)

                    print(request.session["changes_dict"])
                    return JsonResponse({"old_val": old_value, "is_valid": is_valid})
            
            params = None

            if "filter_scope" in request.session.keys() and request.session["filter_scope"]:
                component_id = request.session["filter_scope"]
                params = Parameters.objects.filter(file__instance__app__component_id=component_id).order_by("name")
            else: 
                params = Parameters.objects.all().order_by("name")
            
            if "search_str" in request.session.keys() and request.session["search_str"]:
                search_str = request.session["search_str"]
                params = params.filter(name__icontains=search_str).order_by("name")

            paginatorr = Paginator(params, n_pages)
            results = []
            for par in paginatorr.page(page_n).object_list:
                results.append(par.get_dict_with_all_relative_fields())
            return JsonResponse({"results":results, "num_pages": paginatorr.num_pages, "page_n": page_n})
    else:
        filter_scope = None
        search_str = None
        request.session["changes_dict"] = None
        if "filter_scope" in request.session.keys() and request.session["filter_scope"]:
            filter_scope = int(request.session["filter_scope"])
            component_id = request.session["filter_scope"]
            params = Parameters.objects.filter(file__instance__app__component_id=component_id).order_by("name")
        else: 
            params = Parameters.objects.all().order_by("name")

        if "search_str" in request.session.keys() and request.session["search_str"]:
                search_str = request.session["search_str"]
                params = params.filter(name__icontains=search_str).order_by("name")
        
        paginatorr = Paginator(params, n_pages)

        context = {
        'page_obj': paginatorr.page(1),
        'params': paginatorr.page(1).object_list,
        'components': (
                    Components.objects
                    .values("id", "name")
                    .annotate(cnt=Count("applications__instances__files__parameters"))
                    .filter(cnt__gt=0)
                    .order_by("-cnt")
                ),
        'filter_scope': filter_scope,
        'search_str': search_str,
        }

        return render(request, "config_management/configuration.html", context)

