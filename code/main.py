from setup import *
from seguidor import seguir_linha
from verde import verificar_verde
from sala_3 import verificar_sala3
from pybricks.tools import wait

while True:
    seguir_linha()
    verificar_verde()
    verificar_sala3()
    wait(1)
