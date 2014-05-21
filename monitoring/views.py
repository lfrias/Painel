#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import logging
log = logging.getLogger(__name__)
from django.shortcuts import render
from django.shortcuts import render_to_response

def home(request):
    return render_to_response('painel.html')

LEITURAS = {
                'temperatura': {
                    'interesse': 'temperatura',
                    'valor': 24.5
                },
                'temperatura-falha': {
                    "random string"
                },
                'temperatura-critica': {
                    'interesse': 'temperatura',
                    'valor': 40.0
                }
            }

SENSORES = ['temperatura',]

COND_OP = {'temperatura': {
                'type': 'range',
                'valor': [10.0, 30.0]
            },
            'fumaca': {
                'type': 'bool',
                'valor': [True]
            }}

class FakeModulo:
    def __init__(self, _id):
        self.id = _id
        self.peso= _id

modulos = [FakeModulo(1), FakeModulo(2)]


ATIVO = 0
AGUARDO_DE_CONDICOES = 1
FALHA_DE_OPERACAO = 2
CRITICO = 3

ESTADOS_MODULOS = {
        AGUARDO_DE_CONDICOES: {
            'label': u'Aguardo de Condições',
            'cor': 'blue',
            'peso': 1
            },
        ATIVO: {
            'label': u'Ativo',
            'cor': 'green',
            'peso': 2
            },
        FALHA_DE_OPERACAO: {
            'label': u'Falha de Operação',
            'cor': 'yellow',
            'peso': 3
            },
        CRITICO: {
            'label': u'Crítico',
            'cor': 'red',
            'peso': 4
            }
        }

AGUARDO_DE_CONDICOES_SALA = 0
ATIVO_SALA = 1

class SensorError(Exception):
        pass

class Sala:

    def __init__(self, _id):
        # Qual a sala? Pegar do BD
        self.id = _id
        self._load_cond_op()
        self._load_modulos()
        self._atualizar_estado()

    def get_nome(self):
        return 'H-209'

    def get_peso(self):
        peso = 0
        pesos = [m.peso for m in self.modulos]
        return sum(pesos) / len(pesos)

    def get_mapa_link(self):
        return 'mapa.com'

    def _atualizar_estado(self):
        if not self.condicoes:
            self.estado = AGUARDO_DE_CONDICOES_SALA
        else:
            self.estado = ATIVO_SALA

    def _load_modulos(self):
        self.modulos = []
        #modulos = Modulo.objects.filter(sala=self.id)
        modulos = []
        for _m in modulos:
            m = Modulo(_m.id, self)
            self.modulos.append(m)

    def _load_cond_op(self):
        self.condicoes = COND_OP

    def to_json(self):
        return {
                'label': self.get_nome(),
                'link_to_mapa': self.get_mapa_link(),
                'peso': self.get_peso(),
                'condicoes_operacao': self.condicoes,
                'modulos': [ m.to_json() for m in self.modulos ]
                }

class Modulo:

    def __init__(self, _id, sala):
        self.id = _id
        self.estado = None
        self.sala = sala
        self.leituras = []
        self._processar_leituras()

    @property
    def peso(self):
        return self.estado['peso']

    def _add_leitura(self, leitura):
        self.leituras.append(leitura)

    def _is_critical(self, sensor):
        condicoes = self.sala.condicoes[sensor.name]
        tipo, valor_ref = condicoes['type'], condicoes['valor']
        if tipo == 'bool':
            if bool(sensor.value) != valor_ref[0]:
                return True

        if tipo == 'range':
            valor_min, valor_max = valor_ref
            sensor_value = float(sensor.value)
            if sensor_value < valor_min or sensor_value > valor_max:
                return True

        return False

    def set_estado(self, estado):
        if not self.estado:
            self.estado = ESTADOS_MODULOS[estado].copy()
            return
        novo_estado = ESTADOS_MODULOS[estado]
        if self.estado['label'] != novo_estado['label'] and self.estado['peso'] < novo_estado['peso']:
            self.estado = novo_estado.copy()

    def _atualizar_estado(self):
        for s in self.leituras:
            try:
                s.parse()
            except SensorError:
                self.set_estado(FALHA_DE_OPERACAO)
                return
            if self._is_critical(s):
                self.set_estado(CRITICO)
            else:
                self.set_estado(ATIVO)

    def _processar_leituras(self):
        if self.sala.estado == AGUARDO_DE_CONDICOES_SALA:
            self.set_estado(AGUARDO_DE_CONDICOES)
            return
        for sensor_name in self.get_all_sensores():
            l = Sensor(sensor_name)
            self._add_leitura(l)
            self._atualizar_estado()

    def get_all_sensores(self):
        return SENSORES

    def to_json(self):
        return {
                'label': u'Módulo %02d' % self.id,
                'peso': self.estado['peso'],
                'style': {
                    'cor': self.estado['cor']
                    },
                'sensores': [
                        l.to_json() for l in self.leituras
                    ]
                }

class Sensor:

    def __init__(self, interesse):
        self.interesse = interesse

    def get_leitura(self):
        return LEITURAS[self.interesse]

    def _parse(self):
        leitura = self.get_leitura()
        self.name = leitura['interesse']
        self.value = leitura['valor']

    def parse(self):
        try:
            self._parse()
        except:
            import traceback
            log.debug(u"ERROR: %s" % traceback.format_exc())
            raise SensorError
        if self.name != self.interesse:
            log.debug(u"ERROR: interesse %s não é o mesmo da API %s" % self.name, self.interesse)
            raise SensorError

    def to_json(self):
        return {
                'nome': self.name,
                'valor': self.value
                }
