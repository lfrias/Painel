
LEITURAS = {
                'temperatura': {
                    'interesse': 'temperatura',
                    'valor': '24.5'
                },
                'temperatura-falha': {
                    "random string"
                },
                'temperatura-critica': {
                    'interesse': 'temperatura',
                    'valor': '40.0'
                }
            }


BD = {
        1: {
            'name': 'H-209',
            'condicoes': {
                'temperatura': {
                    'type': 'range',
                    'valor': [10.0, 30.0]
                },
                'fumaca': {
                    'type': 'bool',
                    'valor': [True]
                },
                'umidade': {
                    'type': 'range',
                    'valor': [10, 50]
                }
            },
            'modulos': {
                1: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '24.5'
                        },
                        'umidade': {
                            'interesse': 'umidade',
                            'valor': '30'
                        },
                        'fumaca': {
                            'interesse': 'fumaca',
                            'valor': 'true'
                        },
                    }
                },
                2: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '20'
                        },
                        'umidade': {
                            'interesse': 'umidade-interesse',
                            'valor': '20%'
                        },
                        'fumaca': {
                            "random"
                        }
                    }
                }
            },
        },
        2: {
            'name': 'H-210',
            'condicoes': {
                'temperatura': {
                    'type': 'range',
                    'valor': [10.0, 25.0]
                },
            },
            'modulos': {
                1: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '25.5'
                        },
                        'umidade': {
                            'interesse': 'umidade',
                            'valor': '30%'
                        },
                        'fumaca': {
                            'interesse': 'fumaca',
                            'valor': 'true'
                        },
                    }
                },
                2: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '20'
                        }
                    }
                }
            },
            },
        3: {
            'name': 'H-211',
            'condicoes': {
                'temperatura': {
                    'type': 'range',
                    'valor': [10.0, 25.0]
                },
            },
            'modulos': {
                1: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '25.5'
                        },
                        'umidade': {
                            'interesse': 'umidade',
                            'valor': '30%'
                        }
                    }
                },
                2: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '20'
                        }
                    }
                }
            },
            },
        4: {
            'name': 'H-214',
            'condicoes': None,
            'modulos': {
                1: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '25.5'
                        },
                        'umidade': {
                            'interesse': 'umidade',
                            'valor': '30%'
                        }
                    }
                },
                2: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '20'
                        }
                    }
                }
            },
            },
        5: {
            'name': 'H-219',
            'condicoes': {
                'temperatura': {
                    'type': 'range',
                    'valor': [10.0, 30.0]
                },
            },
            'modulos': {
                1: {
                    'sensores': {
                        'temperatura': {
                            'interesse': 'temperatura',
                            'valor': '20'
                        }
                    }
                }
            },
            },
        }

