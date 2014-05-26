from django.contrib import admin
from monitoring.models import Sala, Modulo, Leitura, CondicaoBool, CondicaoRange

admin.site.register([Sala, Modulo, Leitura, CondicaoBool, CondicaoRange])
