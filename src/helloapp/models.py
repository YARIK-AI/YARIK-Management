from django.db import models
import xml.etree.ElementTree as ET
import re


class Components(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "components"


class Files(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    ftype = models.CharField(max_length=5, blank=True, null=True)
    fencoding = models.CharField(max_length=15, blank=True, null=True)
    gitslug = models.CharField(max_length=1024, blank=True, null=True)
    xslt_gitslug = models.CharField(max_length=1024, blank=True, null=True)
    xsd_gitslug = models.CharField(max_length=1024, blank=True, null=True)
    component = models.ForeignKey(Components, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "files"


class Parameters(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    absxpath = models.TextField(blank=True, null=True)
    attr = models.CharField(max_length=31, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    file = models.ForeignKey(Files, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "parameters"

    def add_to_ET(self, root):
        nodes = self.absxpath.split("/")[1:]
        el = root
        for n in nodes:
            if el.find(n):
                el = el.find(n)
            else:
                if re.match(r'^.+\[@n="\d+"\]$', n):
                    sub_el = ET.Element(
                        n[: n.find("[")], {"n": n[n.find('"') + 1 : n.rfind('"')]}
                    )
                else:
                    sub_el = ET.Element(n)
                el.append(sub_el)
                el = sub_el
        el.text = self.value
        return root
