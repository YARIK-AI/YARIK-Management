from django.contrib import admin

from guardian.admin import GuardedModelAdmin
from .models import Parameter

@admin.register(Parameter)
class ParametersAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name')
    ordering = ('id',)
