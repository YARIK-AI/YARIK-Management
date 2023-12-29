from lxml.etree import XMLParser, XSLT
from xml.etree.ElementTree import Element, fromstring, tostring
from xmlschema import XMLSchema10, XMLSchemaValidationError


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

