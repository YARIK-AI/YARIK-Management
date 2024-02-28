from django.db import models
from lxml.etree import Element, _Element
from re import match
from os.path import join as os_path_join
from guardian.shortcuts import get_perms, assign_perm, remove_perm


class Module(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=31, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "modules"


class Component(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    module = models.ForeignKey(Module, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "components"


class Application(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    component = models.ForeignKey(Component, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "applications"


class Instance(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    version = models.CharField(max_length=31, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    app = models.ForeignKey(Application, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "instances"


class File(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    ftype = models.CharField(max_length=5, blank=True, null=True)
    fencoding = models.CharField(max_length=15, blank=True, null=True)
    path_prefix = models.CharField(max_length=1024, blank=True, null=True)
    gitslug_postfix = models.CharField(max_length=1024, blank=True, null=True)
    xslt_gitslug_postfix = models.CharField(max_length=1024, blank=True, null=True)
    xsd_gitslug_postfix = models.CharField(max_length=1024, blank=True, null=True)
    is_sync = models.BooleanField(blank=False, null=False)
    instance = models.ForeignKey(Instance, models.DO_NOTHING, blank=True, null=True)


    @property
    def gitslug(self):
        return os_path_join(self.path_prefix, self.gitslug_postfix)
    

    @property
    def xslt_gitslug(self):
        return os_path_join(self.path_prefix, self.xslt_gitslug_postfix)
    

    @property
    def xsd_gitslug(self):
        return os_path_join(self.path_prefix, self.xsd_gitslug_postfix)


    def get_xpath_value_dict(self):
        query = self.parameter_set
        xpvd = {}
        for q in query.values("absxpath"):
            xpvd[q["absxpath"]] = query.get(absxpath=q["absxpath"])
        return xpvd


    def get_ET(self) -> _Element:
        root = Element("xml_repr")
        for param in self.parameter_set.order_by("id"):
            root = param.add_to_ET(root)
        return root


    def save_changes(self, items):
        for item in items:
            par = self.parameter_set.filter(id=item["id"]).first()
            if par is not None:
                par.value = item["new_value"]
                par.save()
        self.is_sync = False
        self.save()


    class Meta:
        managed = False
        db_table = "files"


class Parameter(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    absxpath = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    default_value = models.TextField(blank=True, null=True)
    input_type = models.TextField(max_length=14, blank=True, null=True)
    file = models.ForeignKey(File, models.DO_NOTHING, blank=True, null=True)


    def __str__(self):
        return self.name
    

    def get_permission_level(self, group):
        if 'change_parameter' in get_perms(group, self):
            return 'change_parameter'
        elif 'view_parameter' in get_perms(group, self):
            return 'view_parameter'
        else:
            return 'no_permissions'


    def can_view(self, group):
        return 'view_parameter' in get_perms(group, self) or 'change_parameter' in get_perms(group, self)
    

    def can_change(self, group):
        return 'change_parameter' in get_perms(group, self)
    
    def can_nothing(self, group):
        perms = get_perms(group, self)
        return not 'change_parameter' in perms and not 'view_parameter' in perms
    

    def allow_change(self, group):
        perms = get_perms(group, self)
        if 'view_parameter' in perms:
            remove_perm('view_parameter', group, self)
        
        if 'change_parameter' not in perms:
            assign_perm('change_parameter', group, self)

        return 'change_parameter' in perms
    
    def allow_view(self, group):
        perms = get_perms(group, self)
        if 'change_parameter' in perms:
            remove_perm('change_parameter', group, self)

        if 'view_parameter' not in perms:
            assign_perm('view_parameter', group, self)
        
        return 'view_parameter' in perms


    def set_permission_level(self, group, perm_lvl):
        match perm_lvl:
            case 'change_parameter':
                self.allow_change(group)
            case 'view_parameter':
                self.allow_view(group)
            case 'no_permissions':
                self.deny_all(group)


    def deny_all(self, group):
        perms = get_perms(group, self)
        if 'change_parameter' in perms:
            remove_perm('change_parameter', group, self)
        
        if 'view_parameter' in perms:
            remove_perm('view_parameter', group, self)

        return not 'change_parameter' in perms and not 'view_parameter' in perms


    def get_dict_with_all_relative_fields(self, group):
            return {
                        "id": self.id,
                        "name": self.name,
                        "description": self.description,
                        "absxpath": self.absxpath,
                        "value": self.value,
                        "input_type": self.input_type,
                        "default_value": self.default_value, 
                        "file": {
                            "id": self.file.id,
                            "name": self.file.name,
                            "instance": {
                                "id": self.file.instance.id,
                                "name": self.file.instance.name,
                                "app": {
                                    "id": self.file.instance.app.id,
                                    "name": self.file.instance.app.name,
                                    "component": {
                                        "id": self.file.instance.app.component.id,
                                        "name": self.file.instance.app.component.name,
                                    },
                                },
                            },
                        },
                        "can_change": self.can_change(group),
                    }


    def add_to_ET(self, root:_Element):
        nodes = self.absxpath.split("/")[1:]
        el = root
        for n in nodes:
            elem = el.find(n)
            if elem is not None:
                el = elem
            else:
                if match(r'^.+\[@n="\d+"\]$', n):
                    tag = n[: n.find("[")]
                    attr = n[n.find('"') + 1 : n.rfind('"')]
                    sub_el = Element(tag, n=attr)
                else:
                    sub_el = Element(n)
                el.append(sub_el)
                el = sub_el
        el.text = self.value
        return root


    class Meta:
        managed = False
        db_table = "parameters"

