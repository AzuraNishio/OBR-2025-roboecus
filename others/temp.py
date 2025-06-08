# Importando as bibliotecas necessárias do Pybricks
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Direction, Port
from pybricks.tools import wait, StopWatch
from ReLib import *

# --- Inicializações globais ---
hub = PrimeHub()
cronometro = StopWatch()
cronometro_linha = StopWatch()

sensor_direito = ReColor(Port.B)
sensor_esquerdo = ReColor(Port.A)
sensor_frente = ReColor(Port.C)
sensores = ReColorDuo(sensor_esquerdo, sensor_direito)
sonic = UltrasonicSensor(Port.D)

motor_esquerdo = Motor(Port.E)
motor_direito = Motor(Port.F, Direction.COUNTERCLOCKWISE)
base = ReDriveBase(motor_esquerdo, motor_direito, wheel_diameter=38, axle_track=112)

sensor_esquerdo.set_multiplicadores(1, 1, 1, 0.9)
sensor_direito.set_multiplicadores(1, 1, 1, 0.9)

kp, kd, kc = 27, -0.012, -0.1
velocidade_base = 60
velocidade_reta = 100
velocidade_busca = 100
velocidade_fina = 10
fazer_busca = True

limite_busca = 50  # mesa oficial
# limite_busca = 1  # mesa de testes em casa
limiar_preto = 14
margem_cinza = 19
verde = (22, 32, 28)
limiar_verde = 8

# Variáveis de controle
curva_cumulativa = 0
erro = 0
ultimo_tempo = cronometro.time()
tempo_em_linha = 0
angulo_inicio_linha = 0
primeiro_erro_linha = 0
estava_na_linha = False

hub.imu.reset_heading(0)

# --- Funções auxiliares ---


def sair_sala_3_reto(hub, base, sensores, alinhar: bool, u):
    print("[sair_sala_3_reto] Iniciando saída da sala 3, alinhar =", alinhar, ", u =", u)
    if alinhar:
        print("[sair_sala_3_reto] Recuando base em", -1 * u, "mm")
        base.straight(-1 * u)
    else:
        print("[sair_sala_3_reto] Quantizando ângulo para 90 graus")
        quantizar_angulo(hub, 90)

    base.drive(900, 0)
    while sensores.get_sensor_right_if_true(True).rgb()[1] > limiar_preto:
        wait(1)
    print("[sair_sala_3_reto] Linha detectada, parada.")


def quantizar_angulo(hub, step):
    angulo = (hub.imu.heading() + (step / 2)) % step - (step / 2)
    print(f"[quantizar_angulo] Ângulo atual {hub.imu.heading():.2f} quantizado para {angulo:.2f}")
    base.curve(angulo, 0, 20)


def is_tilted(hub):
    tilt_x, tilt_y, *_ = hub.imu.tilt()
    print(f"[is_tilted] tilt_x={tilt_x:.2f}, tilt_y={tilt_y:.2f}")
    return (tilt_x + tilt_y) > 12


# --- Loop principal ---
while True:
    tempo_atual = cronometro.time()
    delta_t = max(0.001, (tempo_atual - ultimo_tempo) / 1000)
    ultimo_tempo = tempo_atual

    # Lógica verde: detecta e reage à cor verde
    if sensor_direito.compare_rgb(verde, limiar_verde) or sensor_esquerdo.compare_rgb(verde, limiar_verde):
        print("[LOG] Detectado verde! Parando para manobra especial.")
        base.straight(5)

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

    # Seguimento da linha
    erro_anterior = erro
    erro = sensores.g_difference()
    erro_quadratico = sensores.g_squared_difference()
    derivada = (erro_anterior - erro) / delta_t
    correcao = erro * kp + derivada * kd



    sinal_correcao = correcao / abs(correcao) if correcao != 0 else 0

    if abs(correcao) > 10:
        if curva_cumulativa == 0 or sinal_correcao == curva_cumulativa / abs(curva_cumulativa):
            curva_cumulativa += sinal_correcao * delta_t * kc
        else:
            curva_cumulativa = 0
    else:
        curva_cumulativa = 0


    if abs(correcao) > 10:
        if abs(correcao) > 35:

            base.drive_with_gyro(velocidade_base, correcao + curva_cumulativa)
        else:

            base.drive(velocidade_reta, correcao + curva_cumulativa)
    else:

        base.drive(velocidade_reta, 0)

    # Busca da linha se perdida


    # Lógica Sala 3
    if sensor_direito.reflection() > 80:
        print("[Sala 3] Condição inicial satisfeita, reflexo do sensor direito:", sensor_direito.reflection())
        lado_do_sensor = 1
        entrada_meio = False
        lado_oposto_do_sensor = -lado_do_sensor
        u = 300  # 1 terço da sala 3 em milímetros
        sonic_limit = 3 * u * pow(2.1, 0.5)

        print(f"[Sala 3] Movendo base para frente {u} mm")
        base.straight(u)
        dist1 = sonic.distance()
        print(f"[Sala 3] Distância detectada pelo ultrassom: {dist1}")

        if dist1 > sonic_limit:
            print("[Sala 3] Distância maior que limite, curva para sair da sala")
            base.curve(lado_do_sensor * -90, 0, velocidade_fina)
            sair_sala_3_reto(hub, base, sensores, not entrada_meio, u)
        else:
            print("[Sala 3] Distância menor ou igual ao limite, lógica alternativa")
            base.curve(lado_do_sensor * -90, 0, velocidade_fina)
            quantizar_angulo(hub, 90)
            base.straight(dist1 - (u * 1.5) + 80)

            if dist1 > u * 1.7 and sonic.distance() > sonic_limit:
                print("[Sala 3] Nova condição satisfeita, saindo reto")
                base.curve(lado_do_sensor * -90, 0, velocidade_fina)
                sair_sala_3_reto(hub, base, sensores, False, u)
            else:
                print("[Sala 3] Curvando para o lado oposto")
                base.curve(lado_do_sensor * 90, 0, velocidade_fina)
                quantizar_angulo(hub, 90)
                base.drive(70, 0)

                while sensor_frente.reflection() < 40 and sonic.distance() < sonic_limit:
                    wait(1)

                base.brake()
                print("[Sala 3] Checando distância frontal")

                if sonic.distance() > sonic_limit:
                    print("[Sala 3] Espaço suficiente para seguir reto")
                    base.straight(u * 0.5)
                    base.curve(lado_do_sensor * -90, 0, velocidade_fina)
                    sair_sala_3_reto(hub, base, sensores, False, u)
                else:
                    print("[Sala 3] Espaço insuficiente, virando 180 graus")
                    base.curve(lado_do_sensor * 180, 0, velocidade_fina)
                    base.drive(50, 0)

                    while sensor_frente.reflection() > 10 or sonic.distance() < sonic_limit:
                        wait(1)

                    base.brake()

                    if sonic.distance() > sonic_limit:
                        print("[Sala 3] Após 180°, espaço liberado, seguindo reto")
                        base.straight(u * 0.5)
                        base.curve(lado_do_sensor * -90, 0, velocidade_fina)
                        sair_sala_3_reto(hub, base, sensores, False, u)
                    else:
                        print("[Sala 3] Ainda sem espaço, virando 180° novamente")
                        base.curve(lado_do_sensor * 180, 0, velocidade_fina)

    wait(1)
