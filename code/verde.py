from setup import base, sensor_direito, sensor_esquerdo, sensores
from constantes import *
from pybricks.tools import wait

def verificar_verde():
    if sensor_direito.compare_rgb(verde, limiar_verde) or sensor_esquerdo.compare_rgb(verde, limiar_verde):
        print("[LOG] Detectado verde! Parando para manobra especial.")
        base.straight(5)

        #isso deve impedir de detectar verde no preto
        if  not (sensor_direito.compare_rgb(verde, limiar_verde) or sensor_esquerdo.compare_rgb(verde, limiar_verde)): return

        verde_direita = sensor_direito.compare_rgb(verde, limiar_verde)
        verde_esquerda = sensor_esquerdo.compare_rgb(verde, limiar_verde)
        print(f"[LOG] Verde Direita: {verde_direita}, Verde Esquerda: {verde_esquerda}")

        while sensor_direito.compare_rgb(verde, limiar_verde) or sensor_esquerdo.compare_rgb(verde, limiar_verde):
            base.drive(velocidade_reta + 109, 0)

        base.straight(6)

        if sensor_esquerdo.rgb()[1] < limiar_preto + margem_cinza or sensor_direito.rgb()[1] < limiar_preto + margem_cinza:
            print("[LOG] Confirmado preto após verde, executando manobra")

            if verde_direita and verde_esquerda:
                print("[LOG] Virada 180 graus")
                base.straight(40)
                base.curve(150, 0, 90)

                base.drive(0, 90)
                while sensor_esquerdo.rgb()[1] > limiar_preto:
                    wait(1)

                base.brake()
                print("[LOG] Virada 180, esperando linha do lado esquerdo")

                base.drive(0, -90)
                while sensor_esquerdo.rgb()[1] < limiar_preto + margem_cinza:
                    wait(1)

                base.curve(-3, 0, velocidade_fina)
                base.straight(-40)
                print("[LOG] Manobra 180 graus concluída")

            else:
                print("[LOG] Virada 90 graus para um dos lados")
                sensor_da_curva = sensores.get_sensor_right_if_true(verde_direita)
                sensor_oposto_da_curva = sensores.get_sensor_right_if_true(verde_esquerda)
                curve_sign = 1 if verde_direita else -1

                base.straight(70)
                base.curve(60 * curve_sign, 0, 90)

                base.drive(0, 90 * curve_sign)
                while sensor_oposto_da_curva.rgb()[1] > limiar_preto:
                    wait(1)

                base.brake()
                print("[LOG] Virada 90 graus, esperando linha do lado oposto")

                base.drive(0, -90 * curve_sign)
                while sensor_oposto_da_curva.rgb()[1] < limiar_preto + margem_cinza:
                    wait(1)

                base.curve(-3 * curve_sign, 0, velocidade_fina)

                base.straight(-30)
                print("[LOG] Manobra 90 graus concluída")
