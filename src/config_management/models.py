from django.db import models
from xml.etree.ElementTree import Element
from re import match


class Components(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "components"


class Files(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    ftype = models.CharField(max_length=5, blank=True, null=True)
    fencoding = models.CharField(max_length=15, blank=True, null=True)
    gitslug = models.CharField(max_length=1024, blank=True, null=True)
    xslt_gitslug = models.CharField(max_length=1024, blank=True, null=True)
    xsd_gitslug = models.CharField(max_length=1024, blank=True, null=True)
    component = models.ForeignKey(Components, models.DO_NOTHING, blank=True, null=True)

    def get_xpath_value_dict(self):
        query = self.parameters_set
        xpvd = {}
        for q in query.values("absxpath"):
            xpvd[q["absxpath"]] = query.get(absxpath=q["absxpath"])
        return xpvd


    def get_ET(self):
        root = Element("xml_repr")
        for param in self.parameters_set.order_by("id"):
            root = param.add_to_ET(root)
        return root


    def save_changes(self, items):
        for item in items:
            par = self.parameters_set.filter(absxpath=item[0]).first()
            if par is not None:
                par.value = item[1]
                par.save()


    class Meta:
        managed = False
        db_table = "files"


class Parameters(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=63, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    absxpath = models.TextField(blank=True, null=True)
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
                if match(r'^.+\[@n="\d+"\]$', n):
                    sub_el = Element(
                        n[: n.find("[")], {"n": n[n.find('"') + 1 : n.rfind('"')]}
                    )
                else:
                    sub_el = Element(n)
                el.append(sub_el)
                el = sub_el
        el.text = self.value
        return root
