from django.db import models


class Edificio(models.Model):
    nome = models.CharField(max_length = 200)
    andar_inicial = models.IntegerField()
    andar_final = models.IntegerField()

    class Meta:
        db_table = "edificio"

class Andar(models.Model):
    numAndar = models.IntegerField()
    planta = models.CharField(max_length = 200)
    edificio = models.ForeignKey(Edificio)

    class Meta:
        db_table = "andar"

class Sala(models.Model):
    nome = models.CharField(max_length = 200)
    posicao_x = models.FloatField()
    posicao_y = models.FloatField()
    andar = models.ForeignKey(Andar)

    class Meta:
    	db_table = 'sala'

    def __str__(self):
    	return self.nome

class Modulo(models.Model):
    id = models.IntegerField(primary_key = True)
    sala = models.ForeignKey(Sala)

    class Meta:
    	db_table = 'modulo'

    def __str__(self):
    	return "Modulo " + str(self.id)

class Leitura(models.Model):
    modulo = models.ForeignKey(Modulo)
    interesse = models.CharField(max_length = 200)
    valor = models.CharField(max_length = 200)
    criado = models.DateTimeField(auto_now_add=True)

    class Meta:
    	db_table = 'leituracritica'

    def __str__(self):
    	return self.interesse + ": " + str(self.valor)

class Estado(models.Model):
	modulo = models.ForeignKey(Modulo)
	nome = models.CharField(max_length = 200)
	criado = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'estado'

class Condicao(models.Model):
    sala = models.ForeignKey(Sala)
    tipo = models.CharField(max_length = 200)
    interesse = models.CharField(max_length = 200)

    class Meta:
        abstract = True

class CondicaoBool(Condicao):
    valor_critico = models.BooleanField()

    class Meta:
    	db_table = 'condicaobool'

    def __str__(self):
        return self.interesse + ": " + str(self.valor_critico)

class CondicaoRange(Condicao):
    min = models.FloatField()
    max = models.FloatField()

    class Meta:
    	db_table = 'condicaorange'

    def __str__(self):
        return self.interesse + ": " + str(self.min) + " - " + str(self.max)
