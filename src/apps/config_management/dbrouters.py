from .models import Module, Component, Application, Instance, File, Parameter


class ModulesDBRouter:
    def db_for_read(self, model, **hints):
        if model == Module:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Module:
            return "artifacts"
        return None


class ComponentsDBRouter:
    def db_for_read(self, model, **hints):
        if model == Component:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Component:
            return "artifacts"
        return None


class ApplicationsDBRouter:
    def db_for_read(self, model, **hints):
        if model == Application:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Application:
            return "artifacts"
        return None


class InstancesDBRouter:
    def db_for_read(self, model, **hints):
        if model == Instance:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Instance:
            return "artifacts"
        return None


class FilesDBRouter:
    def db_for_read(self, model, **hints):
        if model == File:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == File:
            return "artifacts"
        return None


class ParametersDBRouter:
    def db_for_read(self, model, **hints):
        if model == Parameter:
            return "artifacts"
        return None

    def db_for_write(self, model, **hints):
        if model == Parameter:
            return "artifacts"
        return None

