from django.contrib import admin
from polargraph.models import *

admin.site.register(Pipeline)
admin.site.register(DataSource)
admin.site.register(GeneratorState)
admin.site.register(Endpoint)

class ParameterInline(admin.TabularInline):
    model = Parameter

class GeneratorAdmin(admin.ModelAdmin):
    inlines = [
        ParameterInline,
    ]

admin.site.register(Generator,GeneratorAdmin)

