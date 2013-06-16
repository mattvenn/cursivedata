from django.contrib import admin
from polargraph.models import *

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
class PipelineAdmin(admin.ModelAdmin):
    model = Pipeline
    fields = ('img_width','img_height','name','description','generator','endpoint', 'print_top_left_x', 'print_top_left_y', 'print_width', 'sources' )


admin.site.register(Generator,GeneratorAdmin)
admin.site.register(Pipeline,PipelineAdmin)

