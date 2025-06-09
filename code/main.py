from setup import *
from seguidorTeste import seguir_linha
from verde import *
from sala_3 import verificar_sala3
from pybricks.tools import wait
from pybricks.tools import StopWatch
from utils import *




sensores.info_dump()


while True:
    esquerda, direita = teste_verde()
    fazer_verde(esquerda, direita)
    seguir_linha()
    verificar_sala3()

