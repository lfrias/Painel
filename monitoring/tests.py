#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import monitoring.views as mv
from monitoring.views import Modulo, Sensor, Sala

class TestSensor(TestCase):

    def setUp(self):
        #self.sala = Sala(1)
        #self.modulo = Modulo(1, self.sala)
        pass

    def test_parser(self):
        obj = Sensor('temperatura', 1, 1)
        obj.parse()
        self.assertEquals(obj.name, 'temperatura')
        self.assertEquals(obj.value, '24.5')

        obj2 = Sensor('fumaca', 1, 1)
        obj2.parse()
        self.assertEquals(obj2.name, 'fumaca')
        self.assertEquals(obj2.value, 'true')

        obj3 = Sensor('umidade', 1, 2)
        self.assertRaises(mv.SensorError, obj3.parse)

        obj4 = Sensor('fumaca', 1, 2)
        self.assertRaises(mv.SensorError, obj4.parse)

    def test_json(self):
        obj = Sensor('temperatura', 1, 1)
        json = obj.to_json()
        self.assertEquals(sorted(json.keys()), sorted(['nome', 'valor', 'estado']))

class TestSala(TestCase):

    def setUp(self):
        self.sala = Sala(1)
        self.sala_no_cond = Sala(4)

    def test_cond_op(self):
        self.assertTrue(type(self.sala.condicoes) == dict or
                self.sala.condicoes is None)
        self.assertTrue(type(self.sala_no_cond.condicoes) == dict or
                self.sala_no_cond.condicoes is None)

    def test_estado(self):
        self.assertEquals(self.sala.estado, mv.ATIVO_SALA)
        self.assertEquals(self.sala_no_cond.estado, mv.AGUARDO_DE_CONDICOES_SALA)

    def test_peso(self):
        # Modulo 1: ativo
        # Modulo 2: falha
        # Peso: (2 + 3)/2
        self.assertEquals(self.sala.get_peso(), 2.5)
        # Modulo 1: aguardo
        # Modulo 2: aguardo
        # Peso: (1 + 1)/2 = 1
        self.assertEquals(self.sala_no_cond.get_peso(), 1.0)
        # Modulo 1: critico
        # Modulo 2: ativo
        # Peso: (2 + 4)/2
        self.assertEquals(Sala(2).get_peso(), 3.0)

    def test_json(self):
        sala = self.sala.to_json()
        self.assertEquals(sorted(sala.keys()), sorted(['label',
            'link_to_mapa', 'condicoes_operacao','peso', 'modulos']))
        self.assertEquals(sala['label'], 'H-209')
        modulos = sala['modulos']
        self.assertEquals(len(modulos), 2)

class TestModulo(TestCase):

    def setUp(self):
        pass

    def test_sensores(self):
        modulo = Sala(1).get_modulo(1)
        self.assertEquals(sorted(modulo.get_all_sensores()),
                sorted(['temperatura', 'umidade', 'fumaca']))

    def test_estado(self):
        m1 = Sala(1).get_modulo(1)
        self.assertEquals(m1.estado, mv.ESTADOS_MODULOS[mv.ATIVO])

        m2 = Sala(1).get_modulo(2)
        self.assertEquals(m2.estado, mv.ESTADOS_MODULOS[mv.FALHA_DE_OPERACAO])

        m3 = Sala(2).get_modulo(1)
        self.assertEquals(m3.estado, mv.ESTADOS_MODULOS[mv.CRITICO])

        m4 = Sala(4).get_modulo(1)
        self.assertEquals(m4.estado, mv.ESTADOS_MODULOS[mv.AGUARDO_DE_CONDICOES])

    def test_json(self):
        modulo = Sala(1).get_modulo(1)
        json = modulo.to_json()
        self.assertEquals(sorted(json.keys()), sorted(['label', 'sensores', 'estado', 'style']))

