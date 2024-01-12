from .models import Modules, Components, Applications, Instances, Files, Parameters


class ModulesDBRouter:
    def db_for_read(self, model, **hints):
        if model == Modules:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Modules:
            return "artifacts"
        return None


class ComponentsDBRouter:
    def db_for_read(self, model, **hints):
        if model == Components:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Components:
            return "artifacts"
        return None


class ApplicationsDBRouter:
    def db_for_read(self, model, **hints):
        if model == Applications:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Applications:
            return "artifacts"
        return None


class InstancesDBRouter:
    def db_for_read(self, model, **hints):
        if model == Instances:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Instances:
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

