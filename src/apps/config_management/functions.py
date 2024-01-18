from .models import Parameters, Files
from .classes import RepoManager
from core.settings import GIT_URL
from .xml_processing import *


def validate_parameter(request, param:Parameters, new_value):
    file = param.file  # get the file in which the parameter

    root = file.get_ET() # get ET of config file

    root.find(param.absxpath[1:]).text = new_value # change param value

    repo: RepoManager = None
    if "repo_path" in request.session.keys() and request.session["repo_path"]:
        repo = RepoManager(GIT_URL, request.session.get("repo_path"))
    else: 
        repo = RepoManager(GIT_URL)
        request.session["repo_path"] = repo.temp

    # load xsd from repo
    xsd_str = repo.get_file_as_str(file.xsd_gitslug)

    # get xsd
    xsd = get_xml_schema(xsd_str)

    # validate
    error_element = validate_and_get_error(xsd, root)
    
    return error_element is None


def save_changes(request, changes_dict):

    msg = "default"
    files_dict = {}
    for k, par in changes_dict.items(): # create dict {file_id:[ {change_par1}, {change_par2} ]}
        param = Parameters.objects.get(id=par["id"])
        file_id = Parameters.objects.get(id=par["id"]).file.id
        if file_id not in files_dict:
            files_dict[file_id] = []
        files_dict[file_id].append({"id": param.id , "absxpath": param.absxpath, "new_value": par["new_value"]})

    repo: RepoManager = None
    if request.session.get("repo_path"):
        repo = RepoManager(GIT_URL, request.session.get("repo_path"))
    else: 
        repo = RepoManager(GIT_URL)
        request.session["repo_path"] = repo.temp

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