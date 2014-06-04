from django.contrib import admin
from monitoring.models import Edificio, Andar, Sala, Modulo, Leitura, Estado, CondicaoBool, CondicaoRange

admin.site.register([Edificio, Andar, Sala, Modulo, Leitura, Estado, CondicaoBool, CondicaoRange])