from django.db.models import F, Q
from .queryset_annotation import QuerySetType
from .models import Parameter

class SingleChange:
    def __init__(self, id, name, new_value, old_value, is_valid, default_value) -> None:
        self.id = id
        self.name = name
        self.new_value = new_value
        self.old_value = old_value
        self.is_valid = is_valid
        self.default_value = default_value


    @property
    def is_not_valid(self):
        return not self.is_valid
    

    @property
    def is_default(self):
        return self.new_value == self.default_value
    

    @property
    def is_not_default(self):
        return self.new_value != self.default_value


class ChangeManager:
    def __init__(self, changes_dict:dict[str,dict[str,str]] = {}) -> None:
        self.all_changes:dict[str, SingleChange] = {}
        for k, v in changes_dict.items():
            self.all_changes[k] = SingleChange(
                id=v["id"],
                name=v["name"],
                new_value=v["new_value"],
                old_value=v["old_value"],
                is_valid=v["is_valid"],
                default_value=v["default_value"]
            )
    

    @property
    def is_empty(self):
        return len(self.all_changes) == 0
    

    @property
    def is_not_empty(self):
        return len(self.all_changes) > 0


    @property
    def ids(self):
        return list(self.all_changes.keys())
    

    @property
    def changes(self):
        return list(self.all_changes.values())


    @property
    def error_ids(self):
        return list(
            map(
                lambda p: p.id,
                filter(
                    lambda p: p.is_not_valid,
                    self.changes
                )
            )
        )
    

    @property
    def non_default_ids(self):
        return list(
            map(
                lambda p: p.id,
                filter(
                    lambda p: p.is_not_default,
                    self.changes
                )
            )
        )


    @property
    def total(self):
        return len(self.all_changes)
    

    @property
    def total_errors(self):
        return len(
            list(
                filter(
                    lambda p: p.is_not_valid,
                    self.changes
                )
            )
        )
    

    @property
    def total_non_default(self):
        return len(
            list(
                filter(
                    lambda p: p.is_not_default,
                    self.changes
                )
            )
        )


    @property
    def is_all_valid(self):
        return self.total_errors == 0


    @property
    def is_not_all_valid(self):
        return self.total_errors > 0


    def get_change(self, id):
        return self.all_changes.get(id)


    def get_dict(self):
        result = {} 
        for k, v in self.all_changes.items():
            result[k] = {
                "id": v.id,
                "name": v.name,
                "new_value": v.new_value,
                "old_value": v.old_value,
                "is_valid": v.is_valid,
                "default_value": v.default_value 
            }
        return result


    def where_par_in(self, params:QuerySetType[Parameter]):
        new_changes_dict = {}
        if self.is_not_empty:
            for par in params:
                if str(par.id) in self.ids:
                    v = self.get_change(str(par.id))
                    new_changes_dict[str(par.id)] = {
                        "id": v.id,
                        "name": v.name,
                        "new_value": v.new_value,
                        "old_value": v.old_value,
                        "is_valid": v.is_valid,
                        "default_value": v.default_value 
                    }
        return self.__class__(new_changes_dict)


    def get_counts(self, params:QuerySetType[Parameter]) -> tuple[int, int, int, int]:
        total = params.count()
        total_edited = total_not_edited = total_errors = total_non_default = int(0)

        if self.is_not_empty:
            total_edited = self.total
            total_not_edited = total - total_edited
            total_errors = self.total_errors
            non_default_in_db = (
                params
                .filter(~Q(id__in=self.ids)) # id not in list of changed ids
                .filter(~Q(value=F("default_value"))) # column value != column default_value for each parameter
                .count() # count rows
            )
            total_non_default = self.total_non_default + non_default_in_db
        else:
            total_not_edited = total
            # count params where column value != column default_value for each parameter
            total_non_default = params.filter(~Q(value=F("default_value"))).count()
        return (total_edited, total_not_edited, total_errors, total_non_default)