from django.contrib import admin
from polargraph.models import *

admin.site.register(Generator)
admin.site.register(Pipeline)
admin.site.register(DataSource)
admin.site.register(GeneratorState)
admin.site.register(Endpoint)
