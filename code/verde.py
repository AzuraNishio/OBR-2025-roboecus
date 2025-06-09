from setup import base, sensor_direito, sensor_esquerdo, sensores
from constantes import *
from pybricks.tools import wait

def teste_verde() -> tuple[bool, bool]:
    if sensores.is_one_sensor_on_color(verde, limiar_verde):
        print("[LOG] Detectado verde! confirmando leitura.")

        base.straight(2)
        direito = sensor_direito.compare_rgb(verde, limiar_confirmacao_verde)
        esquerdo = sensor_esquerdo.compare_rgb(verde, limiar_confirmacao_verde)

        base.straight(2)
        direito = direito or sensor_direito.compare_rgb(verde, limiar_confirmacao_verde)
        esquerdo = esquerdo or sensor_esquerdo.compare_rgb(verde, limiar_confirmacao_verde)

        base.straight(2)
        direito = direito or sensor_direito.compare_rgb(verde, limiar_confirmacao_verde)
        esquerdo = esquerdo or sensor_esquerdo.compare_rgb(verde, limiar_confirmacao_verde)

        # Impedir alarme em falso causado por preto
        if not (direito or esquerdo):
            print("[LOG] Alarme em falso.")
            return False, False

        verde_direita = sensor_direito.compare_rgb(verde, limiar_verde)
        verde_esquerda = sensor_esquerdo.compare_rgb(verde, limiar_verde)
        print(f"[LOG] Verde Direita: {verde_direita}, Verde Esquerda: {verde_esquerda}")

        while sensor_direito.compare_rgb(verde, limiar_verde) or sensor_esquerdo.compare_rgb(verde, limiar_verde):
            base.drive(velocidade_reta + 109, 0)

        base.straight(6)

        # Confirmar presença de preto após o verde
        if sensor_esquerdo.rgb()[1] < limiar_preto + margem_cinza or sensor_direito.rgb()[1] < limiar_preto + margem_cinza:
            print("[LOG] Confirmado preto após verde")
            return verde_esquerda, verde_direita
        else:
            print("[LOG] Nenhuma linha preta detectada após verde")
            return False, False

    return False, False

def fazer_verde(verde_esquerda, verde_direita):
    if verde_esquerda or verde_direita:
        print("[LOG] Executando manobra após confirmação")

        if verde_direita and verde_esquerda:
            print("[LOG] Virada 180 graus")
            base.straight(40)
            base.curve(150, 0, 90)

            base.drive(0, 90)
            while not sensor_esquerdo.compare_rgb(preto, limiar_preto):
                wait(1)

            base.brake()
            print("[LOG] Virada 180, esperando linha do lado esquerdo")

            base.drive(0, -90)
            while sensor_esquerdo.compare_rgb(preto, limiar_preto + margem_cinza):
                wait(1)

            base.curve(-3, 0, velocidade_fina)
            base.straight(-45)
            print("[LOG] Manobra 180 graus concluída")

        else:
            print("[LOG] Virada 90 graus para um dos lados")
            sensor_oposto_da_curva = sensores.get_sensor_right_if_true(verde_esquerda)
            curve_sign = 1 if verde_direita else -1

            base.straight(70)
            base.curve(60 * curve_sign, 0, 90)

            base.drive(0, 90 * curve_sign)
            while not sensor_oposto_da_curva.compare_rgb(preto, limiar_preto):
                wait(1)

            base.brake()
            print("[LOG] Virada 90 graus, esperando linha do lado oposto")

            base.drive(0, -90 * curve_sign)
            while sensor_oposto_da_curva.compare_rgb(preto, limiar_preto + margem_cinza):
                wait(1)

            base.curve(-3 * curve_sign, 0, velocidade_fina)
            base.straight(-35)
            print("[LOG] Manobra 90 graus concluída")

