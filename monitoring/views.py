#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import logging
log = logging.getLogger(__name__)
from django.shortcuts import render
from django.shortcuts import render_to_response
from bd import BD, LEITURAS

def home(request):
    salas = [Sala(i).to_json() for i in BD.keys()]
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

class SensorError(Exception):
        pass

class Sala:

    def __init__(self, _id):
        self.id = _id
        self.set_cond_op()
        self.set_modulos()
        self.atualizar_estado()

    def get_modulo(self, mid):
        for m in self.modulos:
            if m.id == mid: return m

    def get_nome(self):
        return BD[self.id]['name']

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
        #modulos = Modulo.objects.filter(sala=self.id)
        modulos = BD[self.id]['modulos']
        for mid in modulos:
            m = Modulo(mid, self)
            self.set_estado_modulo(m)
            self.modulos.append(m)

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
                if critico: s.set_estado(CRITICO)
                else:       s.set_estado(ATIVO)
            except KeyError:
                s.set_estado(AGUARDO_DE_CONDICOES)

        modulo.atualizar_estado()
        log.debug(u"Estado do módulo atualizado para: %s" % (modulo.estado['label']))

    def _is_critical(self, sensor):
        condicoes = self.condicoes[sensor.name]
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

    def set_cond_op(self):
        self.condicoes = BD[self.id]['condicoes']

    def to_json(self):
        return {
                'label': self.get_nome(),
                'link_to_mapa': self.get_mapa_link(),
                'peso': self.get_peso(),
                'condicoes_operacao': self.condicoes,
                'modulos': [ m.to_json() for m in self.modulos ]
                }

def get_estado_por_peso(peso):
    for estado in ESTADOS_MODULOS:
        if ESTADOS_MODULOS[estado]['peso'] == peso:
            return estado

class Modulo:

    def __init__(self, _id, sala):
        self.id = _id
        self.estado = ESTADOS_MODULOS[AGUARDO_DE_CONDICOES].copy()
        self.sala = sala
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
        for sensor_name in self.get_all_sensores():
            l = Sensor(sensor_name, self.sala.id, self.id)
            self.leituras.append(l)

    def get_all_sensores(self):
        sensores = BD[self.sala.id]['modulos'][self.id]['sensores']
        log.debug(u"Sensores para módulo %d.%d: %s" % (self.sala.id, self.id, sensores))
        return sensores

    def to_json(self):
        return {
                'label': u'Módulo %02d' % self.id,
                'peso': self.get_peso(),
                'style': {
                    'cor': self.estado['cor']
                    },
                'sensores': [
                        l.to_json() for l in self.leituras
                    ]
                }

class Sensor:

    def __init__(self, interesse, sala_id, modulo_id):
        self.interesse = interesse
        self.estado = ESTADOS_MODULOS[AGUARDO_DE_CONDICOES].copy()
        self.realizar_leitura(sala_id, modulo_id)

    def set_estado(self, estado):
        log.debug(u"Estado para o sensor %s: %s" % (self.interesse,
            ESTADOS_MODULOS[estado]['label']))
        self.estado = ESTADOS_MODULOS[estado].copy()

    def realizar_leitura(self, sala_id, modulo_id):
        self.leitura = BD[sala_id]['modulos'][modulo_id]['sensores'][self.interesse]
        try:
            self.parse()
        except SensorError:
            self.set_estado(FALHA_DE_OPERACAO)

    def _parse(self):
        try:
            self.name = self.leitura['interesse']
            self.value = self.leitura['valor']
        except:
            self.name = self.interesse
            self.value = None
            raise

    def parse(self):
        try:
            self._parse()
        except:
            import traceback
            log.debug(u"ERROR: a leitura retornada não pôde ser traduzida. \
                    \n Leitura: %s \n Erro: %s" % (self.leitura, traceback.format_exc()))
            raise SensorError
        if self.name != self.interesse:
            log.debug(u"ERROR: interesse %s não é o mesmo da API %s" % (self.name, self.interesse))
            raise SensorError

    def to_json(self):
        return {
                'nome': self.name,
                'valor': self.value
                }
