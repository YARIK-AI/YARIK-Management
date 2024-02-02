from django.core.paginator import Paginator
from django.db.models import F, Q, Count
from .models import Parameters, Files, Components
from .classes import RepoManager
from core.settings import GIT_URL
from .xml_processing import *

search_input_xsd = """
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

    <xs:simpleType name="safeString">
        <xs:restriction base="xs:string">
        <xs:pattern value="[a-zA-Z0-9\s]*" />
        </xs:restriction>
    </xs:simpleType>

    <xs:element name="searchInput">
        <xs:complexType>
        <xs:sequence>
            <xs:element name="query" type="safeString" />
        </xs:sequence>
        </xs:complexType>
    </xs:element>

    </xs:schema>
"""

def get_paginator(session):
    filter_scope = int(session.get("filter_scope", "0") or "0")
    filter_status = session.get("filter_status", None)
    search_str = session.get("search_str", None)
    params_per_page = int(session.get("params_per_page", "10") or "10")
    params = Parameters.objects.all().order_by("name")
    changes_dict = session.get("changes_dict", None)

    if filter_scope:
        params = params.filter(file__instance__app__component_id=filter_scope).order_by("name")

    if search_str:
        et = get_et_from_xml_str(f'<searchInput><query>{search_str}</query></searchInput>')
        if(not validate_and_get_error(get_xml_schema(search_input_xsd), et)):
            params = params.filter(name__icontains=search_str).order_by("name")
        else:
            params = Parameters.objects.none()
    
    if filter_status:
        match filter_status:
            case "edited":
                if changes_dict:
                    ids = [v["id"] for k, v in changes_dict.items()]
                    params = params.filter(id__in=ids).order_by("name")
                else:
                    params = Parameters.objects.none()
            case "not_edited":
                if changes_dict:
                    ids = [v["id"] for k, v in changes_dict.items()]
                    params = params.difference(params.filter(id__in=ids).order_by("name"))
            case "error":
                if changes_dict:
                    ids = [v["id"] for k, v in changes_dict.items() if not v["is_valid"]]
                    params = params.filter(id__in=ids).order_by("name")
                else:
                    params = Parameters.objects.none()
            case "non_default":
                if changes_dict:
                    ids = [v["id"] for k, v in changes_dict.items() if v["new_value"] != v["default_value"]]
                    params = params.filter(id__in=ids).order_by("name")
                else:
                    params = params.filter(~Q(value=F("default_value")))

    return Paginator(params, params_per_page)

# need refactoring
def get_scope_filter_items(filter_status=None, changes_dict=None):
    filter_items = { }
    params = None
    
    for c in (Components.objects
        .values("id", "name")
        .annotate(cnt=Count("applications__instances__files__parameters"))
        .filter(cnt__gt=0)
        .order_by("-cnt")):
        filter_items[c["id"]] = { "name": c["name"], "cnt": 0 }

    match filter_status:
        case 'not_edited':
            if changes_dict:
                params = Parameters.objects.filter(~Q(id__in=changes_dict.keys()))
            else: 
                params = Parameters.objects.all()
        case 'edited':
            if changes_dict:
                params = Parameters.objects.filter(id__in=changes_dict.keys())
            else:
                params = Parameters.objects.none()
        case 'error':
            if changes_dict:
                params = Parameters.objects.filter(id__in=[v["id"] for k, v in changes_dict.items() if not v["is_valid"]])
            else:
                params = Parameters.objects.none()
        case 'non_default':
            if changes_dict:
                ids = [v["id"] for k, v in changes_dict.items()]
                default_ids = [v["id"] for k, v in changes_dict.items() if v["new_value"] != v["default_value"]]
                default_ids.extend([p["id"] for p in Parameters.objects.filter(~Q(id__in=ids)).filter(~Q(value=F("default_value"))).values("id")])
                params = Parameters.objects.filter(id__in=default_ids)
            else:
                ids = [p["id"] for p in Parameters.objects.filter(~Q(value=F("default_value"))).values("id")]
                params = Parameters.objects.filter(id__in=ids)
        case _:
            params = Parameters.objects.all()

    for par in params:
        c = par.file.instance.app.component
        filter_items[c.id]["cnt"] = filter_items[c.id]["cnt"] + 1

    return filter_items

# need refactoring, need to filter changes_dict
def get_status_filter_items(filter_scope=None, changes_dict=None):
    filter_items = {
        "edited": { "name": "Edited", "cnt": 0 }, 
        "not_edited": { "name": "Not edited", "cnt": 0 }, 
        "error": { "name": "Error", "cnt": 0 }, 
        "non_default": { "name": "Non-default", "cnt": 0 }
    }

    params = None
    if filter_scope:
        params = Parameters.objects.filter(file__instance__app__component__id=filter_scope)
    else: 
        params = Parameters.objects.all()

    param_cnt = params.count()

    if changes_dict:
        filter_items["edited"]["cnt"] = len(changes_dict)
        filter_items["not_edited"]["cnt"] = param_cnt - filter_items["edited"]["cnt"]
        filter_items["error"]["cnt"] = sum([1 for k, v in changes_dict.items() if not v["is_valid"]])
        filter_items["non_default"]["cnt"] = sum([1 for k, v in changes_dict.items() if v["new_value"] != v["default_value"]])
        ids = [v["id"] for k, v in changes_dict.items()]
        filter_items["non_default"]["cnt"] = filter_items["non_default"]["cnt"] + params.filter(~Q(id__in=ids)).filter(~Q(value=F("default_value"))).count()
    else:
        filter_items["not_edited"]["cnt"] = param_cnt
        filter_items["non_default"]["cnt"] = params.filter(~Q(value=F("default_value"))).count()

    return filter_items


def validate_parameter(session, param:Parameters, new_value):
    file = param.file  # get the file in which the parameter

    root = file.get_ET() # get ET of config file

    root.find(param.absxpath[1:]).text = new_value # change param value

    repo: RepoManager = None
    if session.get("repo_path", None):
        repo = RepoManager(GIT_URL, session.get("repo_path", None))
    else: 
        repo = RepoManager(GIT_URL)
        session["repo_path"] = repo.temp

    # load xsd from repo
    xsd_str = repo.get_file_as_str(file.xsd_gitslug)

    # get xsd
    xsd = get_xml_schema(xsd_str)

    # validate
    error_element = validate_and_get_error(xsd, root)
    
    return error_element is None


def save_changes(session, changes_dict, commit_msg:str=None):

    msg = "default"
    files_dict = {}
    for k, par in changes_dict.items(): # create dict {file_id:[ {change_par1}, {change_par2} ]}
        param = Parameters.objects.get(id=par["id"])
        file_id = Parameters.objects.get(id=par["id"]).file.id
        if file_id not in files_dict:
            files_dict[file_id] = []
        files_dict[file_id].append({"id": param.id , "absxpath": param.absxpath, "new_value": par["new_value"]})

    repo: RepoManager = None
    if session.get("repo_path", None):
        repo = RepoManager(GIT_URL, session.get("repo_path", None))
    else: 
        repo = RepoManager(GIT_URL)
        session["repo_path"] = repo.temp

    xml_files = {}

    for file_id in files_dict.keys(): # iterate by files
        file = Files.objects.get(id=file_id)

        root = file.get_ET() # get ET of config file

        for par in files_dict[file_id]:
            xpath = par["absxpath"][1:]
            value = par["new_value"]
            if xpath.split('/')[-1] == "custom":
                add_custom(root, xpath, value)
            else:
                root.find(xpath).text = value # change param value
        
        # load xsd from repo
        xsd_str = repo.get_file_as_str(file.xsd_gitslug)

        # get xsd
        xsd = get_xml_schema(xsd_str)

        # validate
        error_element = validate_and_get_error(xsd, root)

        if error_element is None:  # if no errors
            # load xslt from repo
            xslt_str = repo.get_file_as_str(file.xslt_gitslug)

            # transform
            result = xslt_transform(xslt_str, root)

            # temporary save file to dict
            xml_files[file_id] = str(result).replace('<?xml version="1.0"?>', "")
        else:
            return f"Validation error in parameter {error_element}"
    
    # overwrite files
    for file_id in xml_files.keys():
        file = Files.objects.get(id=file_id)
        repo.overwrite_file(file.gitslug, xml_files[file_id])

    # commit and push changes if exists and save to db
    if repo.commit_changes(commit_msg):
        file.save_changes(files_dict[file_id])
        msg = "Parameter values successfully changed and committed to git!"
    else:
        msg = "No changes to save!"

    return msg