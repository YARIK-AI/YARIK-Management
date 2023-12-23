from .models import Components, Files, Parameters


class ComponentsDBRouter:
    def db_for_read(self, model, **hints):
        if model == Components:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Components:
            return "artifacts"
        return None


class FilesDBRouter:
    def db_for_read(self, model, **hints):
        if model == Files:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Files:
            return "artifacts"
        return None


class ParametersDBRouter:
    def db_for_read(self, model, **hints):
        if model == Parameters:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Parameters:
            return "artifacts"
        return None
