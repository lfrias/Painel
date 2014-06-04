import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "painel.settings")
from django.conf import settings

from monitoring.models import Edificio, Andar, Sala, Modulo, Leitura, CondicaoBool, CondicaoRange

# adicionando edificio
edificio = Edificio(nome = "Bloco H",
		 andar_inicial = 1,
		 andar_final = 3)
edificio.save()

# adicionando andar
andar = Andar(numAndar = 2,
	  		  planta = "baixa",
	  		  edificio = edificio)
andar.save()

# adicionando salas
andar.sala_set.create(nome = "H-209", posicao_x = 0, posicao_y = 0)
andar.sala_set.create(nome = "H-210", posicao_x = 0, posicao_y = 1)
andar.sala_set.create(nome = "H-211", posicao_x = 0, posicao_y = 2)
andar.sala_set.create(nome = "H-214", posicao_x = 1, posicao_y = 0)
andar.sala_set.create(nome = "H-219", posicao_x = 1, posicao_y = 1)

# pegando salas adicionadas
salas = Sala.objects.all()

# adicionando condicoes H-209
salas[0].condicaorange_set.create(interesse="temperatura",
								  tipo="range",
								  min=10.0, max = 40.0)
salas[0].condicaobool_set.create(interesse="fumaca",
							     tipo="bool",
								 valor_critico = True)
salas[0].condicaorange_set.create(interesse="umidade",
							      tipo="range",
								  min=10.0, max = 50.0)

# adicionando condicoes H-210
salas[1].condicaorange_set.create(interesse="temperatura",
								  tipo="range",
								  min=10.0, max = 25.0)

# adicionando condicoes sala H-211
salas[2].condicaorange_set.create(interesse="temperatura",
							      tipo="range",
								  min=10.0, max = 25.0)

# adicionando condicoes sala H-219
salas[4].condicaorange_set.create(interesse="temperatura",
							      tipo="range",
								  min=10.0, max = 30.0)

# adicionando modulos
salas[0].modulo_set.create(id=1)
salas[0].modulo_set.create(id=2)
salas[1].modulo_set.create(id=3)
salas[1].modulo_set.create(id=4)
salas[2].modulo_set.create(id=5)
salas[2].modulo_set.create(id=6)
salas[3].modulo_set.create(id=7)
salas[3].modulo_set.create(id=8)
salas[4].modulo_set.create(id=9)