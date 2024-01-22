from django.core.paginator import Paginator
from .models import Parameters, Files
from .classes import RepoManager
from core.settings import GIT_URL
from .xml_processing import *


def get_paginator(session, n_pages = 10):
    filter_scope = int(session.get("filter_scope", "0") or "0")
    filter_status = session.get("filter_status", None)
    search_str = session.get("search_str", None)
    params = Parameters.objects.all().order_by("name")

    if filter_scope:
        params = params.filter(file__instance__app__component_id=filter_scope).order_by("name")

    if search_str:
        params = params.filter(name__icontains=search_str).order_by("name")
    
    if filter_status:
        match filter_status:
            case "edited":
                ids = [v.id for k, v in session.get("changes_dict", None).items()]
                params = params.filter(id__in=ids).order_by("name")
            case "not_edited":
                ids = [v.id for k, v in session.get("changes_dict", None).items()]
                params = params.difference(params.filter(id__in=ids).order_by("name"))
            case "error":
                ids = [v.id for k, v in session.get("changes_dict", None).items() if not v["is_valid"]]
                params = params.filter(id__in=ids).order_by("name")
            case "non_default":
                pass

    return Paginator(params, n_pages)


def get_status_dict(changes_dict=None):
    status_dict = {"edited": 0, "not_edited": 0, "error": 0, "non_default": 0}

    param_cnt = Parameters.objects.all().count()

    if changes_dict:
        status_dict["edited"] = len(changes_dict)
        status_dict["not_edited"] = param_cnt - status_dict["edited"]
        status_dict["error"] = sum([1 for k, v in changes_dict.items() if not v["is_valid"]])
    else:
        status_dict["not_edited"] = param_cnt
        
    return status_dict


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


def save_changes(session, changes_dict):

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
    if repo.commit_changes():
        file.save_changes(files_dict[file_id])
        msg = "Parameter values successfully changed and committed to git!"
    else:
        msg = "No changes to save!"

    return msg