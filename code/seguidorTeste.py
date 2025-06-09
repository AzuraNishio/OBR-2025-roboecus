from setup import hub, base, sensores, cronometro, cronometro_linha, sensor_direito, sensor_esquerdo
from constantes import *
from pybricks.tools import wait, StopWatch
from verde import *

curva_cumulativa = 0
erro = 0
ultimo_tempo = cronometro.time()
tempo_em_linha = 0
angulo_inicio_linha = 0
primeiro_erro_linha = 0
direito_estava_na_linha = False
esquerdo_estava_na_linha = False
buscar = False

cronometro_esquerdo = StopWatch()
cronometro_direito = StopWatch()

curve_dir = 0

def seguir_linha():
    global erro, ultimo_tempo, curva_cumulativa, direito_estava_na_linha, esquerdo_estava_na_linha, primeiro_erro_linha, curve_dir, cronometro_esquerdo, cronometro_direito, buscar

    erro = sensores.g_squared_difference()
    speed = 70 - abs(erro)
    correction = erro * 3

    base.drive(speed, correction)

    value = 20

    if sensor_direito.compare_rgb(preto, limiar_preto):
        direito_estava_na_linha = True
        if cronometro_esquerdo.time() > value:
            buscar = True
            lado = 1
    else:
        direito_estava_na_linha = False
        cronometro_direito.reset()

    if sensor_esquerdo.compare_rgb(preto, limiar_preto):
        esquerdo_estava_na_linha = True
        if cronometro_direito.time() > value and not buscar:
            buscar = True
            lado = -1
    else:
        esquerdo_estava_na_linha = False
        cronometro_esquerdo.reset()

    if buscar:
        base.straight(7)
        esquerda, direita = teste_verde()
        if esquerda or direita:
            fazer_verde(esquerda, direita)
        else:
            base.brake()
            lado_direito = lado > 0
            base.straight(63)
            if lado != 0:
                base.drive(0, velocidade_busca * lado)
                while not sensores.get_sensor_right_if_true(not lado_direito).compare_rgb(preto, limiar_preto):
                    wait(1)

                base.drive(0, -velocidade_busca * lado)
                while sensores.get_sensor_right_if_true(not lado_direito).compare_rgb(preto, limiar_preto):
                    wait(1)

                base.straight(-25)

                while sensores.get_sensor_right_if_true(not lado_direito).compare_rgb(preto, limiar_preto):
                    base.drive(0, velocidade_busca * lado)
                    wait(1)

                base.brake()
            buscar = False



