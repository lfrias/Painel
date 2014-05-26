#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import logging
log = logging.getLogger(__name__)
from django.shortcuts import render
from django.shortcuts import render_to_response
from api import API
from monitoring.models import Sala, Modulo, Leitura, CondicaoBool, CondicaoRange


def home(request):
    # Pega modelos do banco de dados e inicializa objetos correspondentes
    salas = [SalaControl(sala_db).to_json() for sala_db in Sala.objects.all()]

    # Dicionario que sera enviado para o template html
    # contendo todos os dados para exibicao
    salas = sorted(salas, key=lambda k: k['peso'], reverse=True)
    return render_to_response('painel.html', {'salas': salas})


ATIVO = 0
AGUARDO_DE_CONDICOES = 1
FALHA_DE_OPERACAO = 2
CRITICO = 3

AGUARDO_DE_CONDICOES_SALA = 0
ATIVO_SALA = 1

ESTADOS_MODULOS = {
        AGUARDO_DE_CONDICOES: {
            'label': u'Aguardo de Condições',
            'html_class': 'panel-info',
            'peso': 1
            },
        ATIVO: {
            'label': u'Ativo',
            'html_class': 'panel-success',
            'peso': 2
            },
        FALHA_DE_OPERACAO: {
            'label': u'Falha de Operação',
            'html_class': 'panel-warning',
            'peso': 3
            },
        CRITICO: {
            'label': u'Crítico',
            'html_class': 'panel-danger',
            'peso': 4
            }
        }

class SensorError(Exception):
        pass

class SalaControl:

    def __init__(self, sala_db):
        self.id = sala_db.id
        self.nome = sala_db.nome
        self.condicoes = {}
        self.set_cond_op()
        self.set_modulos()
        self.atualizar_estado()

    def get_modulo(self, mid):
        for m in self.modulos:
            if m.id == mid: return m

    def get_nome(self):
        return self.nome

    def get_peso(self):
        peso = 0
        pesos = [m.get_peso() for m in self.modulos]
        return sum(pesos) / len(pesos)

    def get_mapa_link(self):
        return 'mapa.com/show?id=%s' % self.id

    def atualizar_estado(self):
        if not self.condicoes:
            self.estado = AGUARDO_DE_CONDICOES_SALA
        else:
            self.estado = ATIVO_SALA

    def set_modulos(self):
        self.modulos = []
        modulos_db = Modulo.objects.filter(sala=self.id)
        for mod_db in modulos_db:
            mod_control = ModuloControl(mod_db, self)
            self.set_estado_modulo(mod_control)
            self.modulos.append(mod_control)

    def set_estado_modulo(self, modulo):
        log.debug("Definindo estado para o módulo %d.%d" % (self.id, modulo.id))
        for s in modulo.leituras:
            if s.estado == ESTADOS_MODULOS[FALHA_DE_OPERACAO]:
                continue

            if not self.condicoes:
                s.set_estado(AGUARDO_DE_CONDICOES)
                continue

            try:
                critico = self._is_critical(s)
                if critico: 
                    s.set_estado(CRITICO)
                    # salva leitura critica no BD
                    Leitura(modulo=Modulo.objects.get(id=modulo.id), 
                            interesse=s.interesse, 
                            valor=s.valor).save()
                else:       
                    s.set_estado(ATIVO)
            except KeyError:
                s.set_estado(AGUARDO_DE_CONDICOES)

        modulo.atualizar_estado()
        log.debug(u"Estado do módulo atualizado para: %s" % (modulo.estado['label']))

    def _is_critical(self, sensor):
        condicao = self.condicoes[sensor.interesse]

        if condicao.tipo == 'bool':
            if bool(sensor.valor) == condicao.valor_critico:
                return True

        if condicao.tipo == 'range':
            if float(sensor.valor) < condicao.min or float(sensor.valor) > condicao.max:
                return True

        return False

    def set_cond_op(self):
        # Inclui as condicoes booleanas e de range num dicionario
        # em que a chave eh o interesse da condicao
        for condicao in CondicaoBool.objects.filter(sala=self.id):
            self.condicoes[condicao.interesse] = condicao
        for condicao in CondicaoRange.objects.filter(sala=self.id):
            self.condicoes[condicao.interesse] = condicao

    def to_json(self):
        modulos = [ m.to_json() for m in self.modulos ]
        modulos = sorted(modulos, key=lambda k: k['estado']['peso'], reverse=True)
        return {
                'id': self.id,
                'label': self.get_nome(),
                'link_to_mapa': self.get_mapa_link(),
                'peso': self.get_peso(),
                'condicoes_operacao': self.conditions_to_json(),
                'modulos': modulos
                }

    def conditions_to_json(self):
        # Converte os objetos Condition em um dicionario
        # que pode ser entendido no template
        cond_dict = {}
        for cond_name in self.condicoes:
            cond = self.condicoes[cond_name]
            if cond.tipo == 'bool':
                cond_dict[cond_name] = {
                                        'tipo': cond.tipo,
                                        'valor': cond.valor_critico
                                       }
            else:
                cond_dict[cond_name] = {
                                        'tipo': cond.tipo,
                                        'valor': [cond.min, cond.max]
                                       }
        return cond_dict


class ModuloControl:

    def __init__(self, mod_db, sala_control):
        self.id = mod_db.id
        self.sala = sala_control
        self.estado = ESTADOS_MODULOS[AGUARDO_DE_CONDICOES].copy()
        self.leituras = []
        self.processar_leituras()

    def get_peso(self):
        return self.estado['peso']

    def atualizar_estado(self):
        pesos = [s.estado['peso'] for s in self.leituras]
        log.debug(u"Pesos dos sensores do módulo %d.%d: %s" %
                (self.id, self.sala.id, pesos))
        maior_peso = max(pesos)
        if self.estado['peso'] < maior_peso:
            estado = get_estado_por_peso(maior_peso)
            self.estado = ESTADOS_MODULOS[estado].copy()

    def processar_leituras(self):
        # Pega os sensores do dicionario em API.py
        sensores = self.get_all_sensores()
        for nome_sensor in sensores.keys():
            # Instancia um objeto SensorControl para cada sensor
            l = SensorControl(nome_sensor, sensores[nome_sensor], self)
            self.leituras.append(l)

    def get_all_sensores(self):
        sensores = API[self.id]['sensores']
        log.debug(u"Sensores para módulo %d.%d: %s" % (self.sala.id, self.id, sensores))
        return sensores

    def to_json(self):
        sensores = [l.to_json() for l in self.leituras]
        sensores = sorted(sensores, key=lambda k: k['estado']['peso'], reverse=True)
        return {
                'id': self.id,
                'label': u'Módulo %02d' % self.id,
                'estado': self.estado,
                'sensores': sensores
                }

class SensorControl:

    def __init__(self, nome, leitura, modulo_control):
        self.modulo = modulo_control
        self.nome = nome
        self.leitura = leitura
        self.estado = ESTADOS_MODULOS[AGUARDO_DE_CONDICOES].copy()
        self.realizar_leitura()

    def set_estado(self, estado):
        log.debug(u"Estado para o sensor %s: %s" % (self.interesse,
            ESTADOS_MODULOS[estado]['label']))
        self.estado = ESTADOS_MODULOS[estado].copy()

    def realizar_leitura(self):
        try:
            self.parse()
        except SensorError:
            self.set_estado(FALHA_DE_OPERACAO)

    def _parse(self):
        try:
            self.interesse = self.leitura['interesse']
            self.valor = self.leitura['valor']
        except:
            self.interesse = self.nome
            self.valor = None
            raise

    def parse(self):
        try:
            self._parse()
        except:
            import traceback
            log.debug(u"ERROR: a leitura retornada não pôde ser traduzida. \
                    \n Leitura: %s \n Erro: %s" % (self.leitura, traceback.format_exc()))
            raise SensorError
        if self.nome != self.interesse:
            log.debug(u"ERROR: interesse %s não é o mesmo da API %s" % (self.nome, self.interesse))
            raise SensorError

    def to_json(self):
        return {
                'nome': self.interesse,
                'valor': self.valor,
                'estado': self.estado,
                }

def get_estado_por_peso(peso):
    for estado in ESTADOS_MODULOS:
        if ESTADOS_MODULOS[estado]['peso'] == peso:
            return estado
