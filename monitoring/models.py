from django.db import models


class Sala(models.Model):
    nome = models.CharField(max_length = 200)

    def __str__(self):
    	return self.nome

class Modulo(models.Model):
    id = models.IntegerField(primary_key = True)
    sala = models.ForeignKey(Sala)

    def __str__(self):
    	return "Modulo " + str(self.id)

class Leitura(models.Model):
    modulo = models.ForeignKey(Modulo)
    interesse = models.CharField(max_length = 200)
    valor = models.CharField(max_length = 200)

    def __str__(self):
    	return self.interesse + ": " + str(self.valor)

class Condicao(models.Model):
    sala = models.ForeignKey(Sala)
    tipo = models.CharField(max_length = 200)
    interesse = models.CharField(max_length = 200)

    class Meta:
        abstract = True

class CondicaoBool(Condicao):
    valor_critico = models.BooleanField()

    def __str__(self):
        return self.interesse + ": " + str(self.valor_critico)

class CondicaoRange(Condicao):
    min = models.FloatField()
    max = models.FloatField()

    def __str__(self):
        return self.interesse + ": " + str(self.min) + " - " + str(self.max)
