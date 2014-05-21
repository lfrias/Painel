#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import monitoring.views as mv
from monitoring.views import Modulo, Sensor, Sala

class TestSensor(TestCase):

    def setUp(self):
        self.sala = Sala(1)
        self.modulo = Modulo(self.sala)
        self.obj = Sensor('temperatura')
        self.obj.parse()

    def test_parser(self):
        self.assertEquals(self.obj.name, 'temperatura')
        self.assertEquals(self.obj.value, '24.5')

    def test_fail_state(self):
        modulo = Modulo(self.sala)
        obj = Sensor('temperatura-falha')
        self.assertRaises(mv.ParseError, obj.parse)

    def test_json(self):
        json = self.obj.to_json()
        self.assertEquals(sorted(json.keys()), sorted(['nome', 'valor']))

class TestSala(TestCase):

    def setUp(self):
        self.sala = Sala(1)
        self.sala_no_cond = Sala(2)

    def test_cond_op(self):
        self.assertTrue(type(self.sala.condicoes) == dict or
                self.sala.condicoes is None)
        self.assertTrue(type(self.sala_no_cond.condicoes) == dict or
                self.sala_no_cond.condicoes is None)

    def test_estado(self):
        self.assertEquals(self.sala.estado, mv.ATIVO_SALA)
        self.assertEquals(self.sala_no_cond.estado, mv.AGUARDO_DE_CONDICOES_SALA)

    def test_peso(self):
        self.assertEquals(self.sala.get_peso(), 2.0)
        self.assertEquals(self.sala_no_cond.get_peso(), 2.0)

    def test_json(self):
        sala = self.sala.to_json()
        self.assertEquals(sorted(sala.keys()), sorted(['label',
            'link_to_mapa', 'condicoes_operacao','peso', 'modulos']))
        self.assertEquals(sala['label'], 'H-209')
        self.assertEquals(sala['condicoes_operacao'], mv.COND_OP)
        modulos = sala['modulos']
        self.assertEquals(len(modulos), 1)

class TestModulo(TestCase):

    def setUp(self):
        self.sala = Sala(1)
        self.modulo = self.sala.modulos[0]

    def test_sensores(self):
        self.assertEquals(self.modulo.get_all_sensores(), ['temperatura'])

    def test_estado(self):
        self.assertEquals(self.modulo.estado, mv.ESTADOS_MODULOS[mv.ATIVO])

    def test_peso(self):
        self.assertEquals(self.modulo.peso, mv.ESTADOS_MODULOS[mv.ATIVO]['peso'])

    def test_json(self):
        json = self.modulo.to_json()
        self.assertEquals(sorted(json.keys()), sorted(['label', 'sensores', 'peso', 'style']))
