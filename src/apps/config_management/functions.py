from django.core.paginator import Paginator
from django.db.models import F, Q, Count
from core.settings import GIT_URL
from .models import Parameter, File, Component
from .RepoManager import RepoManager
from .xml_processing import *
from .ChangeManager import ChangeManager
from django.contrib.auth.models import User
from guardian.shortcuts import get_objects_for_user

import logging

logger = logging.getLogger(__name__)


def get_paginator(user_id:int, filter_scope=0, filter_status=None, search_str=None, params_per_page=10, changes_dict=None):
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

    
    user = User.objects.get(id=user_id)

    params = Parameter.objects.all()

    for par in params: # check perms
        if par.can_nothing(user):
            params = params.exclude(id=par.id)
    logger.info(f"The list of parameters is filtered based on the current user's permissions")


    change_manager = ChangeManager(changes_dict or dict())

    if filter_scope:
        params = params.filter(file__instance__app__component_id=filter_scope)
        logger.info(f'Scope filter "{filter_scope}" applied.')

    if search_str:
        et = get_et_from_xml_str(f'<searchInput><query>{search_str}</query></searchInput>')
        if not validate_and_get_error(get_xml_schema(search_input_xsd), et):
            params = params.filter(name__icontains=search_str)
            logger.info(f'Search text "{search_str}" applied.')
        else:
            params = Parameter.objects.none()
            logger.warning(f'The search text was not applied because it contained prohibited characters!')
    
    if filter_status:
        match filter_status:
            case "edited":
                if change_manager.is_not_empty:
                    params = params.filter(id__in=change_manager.ids)
                else:
                    params = Parameter.objects.none()      
            case "not_edited":
                if change_manager.is_not_empty:
                    params = params.difference(params.filter(id__in=change_manager.ids))
            case "error":
                if change_manager.is_not_empty:
                    params = params.filter(id__in=change_manager.error_ids)
                else:
                    params = Parameter.objects.none()
            case "non_default":
                if change_manager.is_not_empty:
                    params = params.filter(id__in=change_manager.non_default_ids)
                    qs_not_in_changes = Parameter.objects.filter(~Q(id__in=change_manager.ids))
                    qs_not_in_changes_non_default = qs_not_in_changes.filter(~Q(value=F("default_value")))
                    params = params.union(qs_not_in_changes_non_default)
                else:
                    params = params.filter(~Q(value=F("default_value")))
        logger.info(f'Status filter "{filter_status}" applied.')

    if params:
        params = params.order_by("name")
        logger.info(f'Resulting SQL query after applying filters: `{params.query}`.')

    return Paginator(params, params_per_page)

# need refactoring
def get_scope_filter_items(user_id:int, filter_status=None, changes_dict=None):
    filter_items = { }
    params = Parameter.objects.all()

    user = User.objects.get(id=user_id)

    for par in params: # check perms
        if par.can_nothing(user):
            params = params.exclude(id=par.id)

    change_manager = ChangeManager(changes_dict or dict())
    
    for c in (
        Component.objects
        .values("id", "name") # select id, name
        .annotate(cnt=Count("application__instance__file__parameter")) # count params
        .filter(cnt__gt=0) # havind cnt > 0
    ):
        filter_items[c["id"]] = { "name": c["name"], "cnt": 0 }

    if filter_status:
        match filter_status:
            case 'not_edited':
                if change_manager.is_not_empty:
                    params = params.filter(~Q(id__in=change_manager.ids))
                else: 
                    params = params.all()
            case 'edited':
                if change_manager.is_not_empty:
                    params = params.filter(id__in=change_manager.ids)
                else:
                    params = Parameter.objects.none()
            case 'error':
                if change_manager.is_not_empty:
                    params = params.filter(id__in=change_manager.error_ids)
                else:
                    params = Parameter.objects.none()
            case 'non_default':
                if change_manager.is_not_empty:
                    qs_in_changes_non_default = params.filter(id__in=change_manager.non_default_ids)
                    qs_not_in_changes = params.filter(~Q(id__in=change_manager.ids))
                    qs_not_in_changes_non_default = qs_not_in_changes.filter(~Q(value=F("default_value")))
                    params = qs_in_changes_non_default.union(qs_not_in_changes_non_default)
                else:
                    params = params.filter(~Q(value=F("default_value")))
        logger.info(f'Cross-filtering of the scope filter by the status filter "{filter_status}" occurred.')
    else:
        params = params.all()
    
    logger.info(f'Resulting SQL query: `{params.query}`.')

    for par in params:
        c = par.file.instance.app.component
        filter_items[c.id]["cnt"] = filter_items[c.id]["cnt"] + 1
    
    return filter_items


def get_status_filter_items(user_id:int, filter_scope=None, changes_dict=None):
    filter_items = {
        "edited": { "name": "Edited", "cnt": 0 }, 
        "not_edited": { "name": "Not edited", "cnt": 0 }, 
        "error": { "name": "Error", "cnt": 0 }, 
        "non_default": { "name": "Non-default", "cnt": 0 }
    }
    params = Parameter.objects.all()

    user = User.objects.get(id=user_id)

    for par in params: # check perms
        if par.can_nothing(user):
            params = params.exclude(id=par.id)

    change_manager = ChangeManager(changes_dict or dict())

    if filter_scope:
        params = params.filter(file__instance__app__component__id=filter_scope)
        change_manager = change_manager.where_par_in(params)
        logger.info(f'Cross-filtering of the status filter by the scope filter "{filter_scope}" occurred.')
    else: 
        params = params.all()

    total_edited, total_not_edited, total_errors, total_non_default = change_manager.get_counts(params)

    filter_items["edited"]["cnt"] = total_edited
    filter_items["not_edited"]["cnt"] = total_not_edited
    filter_items["error"]["cnt"] = total_errors
    filter_items["non_default"]["cnt"] = total_non_default

    return filter_items


def validate_parameter(repo_path:str, param:Parameter, new_value):
    file = param.file  # get the file in which the parameter

    root = file.get_ET() # get ET of config file

    root.find(param.absxpath[1:]).text = new_value # change param value

    repo = RepoManager(GIT_URL, repo_path)

    # load xsd from repo
    xsd_str = repo.get_file_as_str(file.xsd_gitslug)

    # get xsd
    xsd = get_xml_schema(xsd_str)

    # validate
    error_element = validate_and_get_error(xsd, root)
    
    return error_element is None


def save_changes(repo_path:str, changes_dict:dict[str,dict[str,str]] = {}, commit_msg:str=None):

    msg = "No changes occurred!"
    files_dict = {}
    xml_files = {}
    repo = RepoManager(GIT_URL, repo_path)

    try:
        for par in changes_dict.values(): # create dict {file_id:[ {change_par1}, {change_par2} ]}
            param = Parameter.objects.get(id=par["id"])
            file_id = Parameter.objects.get(id=par["id"]).file.id
            if file_id not in files_dict:
                files_dict[file_id] = []
            files_dict[file_id].append({"id": param.id , "absxpath": param.absxpath, "new_value": par["new_value"]})
    except Exception as e:
        logger.error(f'Error while preparing data before applying changes! {e}')  

    try:
        for file_id in files_dict.keys(): # iterate by files
            file = File.objects.get(id=file_id)

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
        logger.info('Changes applied.')
    except Exception as e:
        logger.error(f'Error while applying changes! {e}')

    # overwrite files
    try:
        for file_id in xml_files.keys():
            file = File.objects.get(id=file_id)
            repo.overwrite_file(file.gitslug, xml_files[file_id])
        logger.info('Files overwritten.')
    except Exception as e:
        logger.error(f'Error while overwriting files! {e}')

    # commit and push changes if exists and save to db
    try:    
        if repo.commit_changes(commit_msg):
            file.save_changes(files_dict[file_id])
            msg = "Parameter values have been successfully changed and committed to git!"
            logger.info('Changes committed to git.')
        else:
            msg = "No changes to save!"
    except Exception as e:
        logger.error(f'Error while committing changes to git! {e}')

    return msg