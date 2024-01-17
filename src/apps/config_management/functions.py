from lxml.etree import XMLParser, XSLT
from xml.etree.ElementTree import Element, fromstring, tostring
from xmlschema import XMLSchema10, XMLSchemaValidationError

from .models import Parameters
from .classes import RepoManager
from core.settings import GIT_URL


def get_xml_schema(xml_str:str, encoding:str='utf-8'):
    parser = XMLParser(ns_clean=True, recover=True, encoding=encoding)
    xml_et = fromstring(xml_str, parser=parser)
    return XMLSchema10(xml_et)


def xslt_transform(xslt_str:str, element_to_transform:Element, encoding:str='utf-8'):
    parser = XMLParser(ns_clean=True, recover=True, encoding=encoding)
    xslt_et = fromstring(xslt_str, parser=parser)
    transform = XSLT(xslt_et)
    return transform(element_to_transform)


def get_xml_str_from_et(_from:Element, encoding:str='utf-8'):
    return f'<?xml version="1.0" encoding="{encoding.upper()}"?>' + tostring(
                _from, encoding
            ).decode(encoding)


def get_et_from_xml_str(_from:str, encoding:str='utf-8'):
    parser = XMLParser(ns_clean=True, recover=True, encoding=encoding)
    return fromstring(_from, parser=parser)


def validate_and_get_error(xml_schema:XMLSchema10, elemenent_to_validate:Element):
    elem = None
    try:
        xml_schema.validate(elemenent_to_validate)
    except XMLSchemaValidationError as e:
        elem = e.path.removeprefix(f"/{e.root.tag}")
        if elem.find("[") > 0 and elem.rfind("]") > 0:
            attr = '[@n="{id}"]'.format(id=elem[elem.find('[')+1:elem.rfind(']')])
            elem = elem[: elem.find("[")] + attr + elem[elem.rfind("]") + 1:]
    return elem


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

