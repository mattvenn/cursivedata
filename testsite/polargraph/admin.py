from django.contrib import admin
from polargraph.models import *

admin.site.register(Pipeline)
admin.site.register(DataStore)
admin.site.register(GeneratorState)
admin.site.register(Endpoint)
admin.site.register(COSMSource)

class ParameterInline(admin.TabularInline):
    model = Parameter

class GeneratorAdmin(admin.ModelAdmin):
    inlines = [
        ParameterInline,
    ]

admin.site.register(Generator,GeneratorAdmin)

