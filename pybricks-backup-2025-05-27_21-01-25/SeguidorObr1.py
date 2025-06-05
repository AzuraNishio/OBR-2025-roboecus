# Importando as bibliotecas necessárias do Pybricks
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Direction, Port
from pybricks.tools import wait, StopWatch
from ReLib import *

# Inicializa o hub e os cronômetros
hub = PrimeHub()
cronometro = StopWatch()
cronometro_linha = StopWatch()

# Sensores de cor
sensor_direito = ReColor(Port.B)
sensor_esquerdo = ReColor(Port.A)
sensores = ReColorDuo(sensor_esquerdo, sensor_direito)

# Motores
motor_esquerdo = Motor(Port.E)
motor_direito = Motor(Port.F, Direction.COUNTERCLOCKWISE)

# Base de movimentação personalizada
base = ReDriveBase(motor_esquerdo, motor_direito, wheel_diameter=38, axle_track=112)

# multiplicadores sensores de cor
sensor_esquerdo.set_multiplicadores()
sensor_direito.set_multiplicadores()

# Parâmetros PIC
kp = 25
kd = -0.012
kc = -0.06

# Velocidades
velocidade_base = 75
velocidade_reta = 120
velocidade_busca = 100
velocidade_fina = 10
fazer_busca = True

# Limiares
limite_busca = 50  # mesa oficial
# limite_busca = 1 #mesa de testes em casa
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
estava_na_linha: bool = False

# Zera o giroscópio
hub.imu.reset_heading(0)

# while True:
#   print(sensor_direito.rgb())

# Loop principal
while True:
    tempo_atual = cronometro.time()
    delta_t = max(0.001, (tempo_atual - ultimo_tempo) / 1000)
    ultimo_tempo = tempo_atual

    # Antes de tudo executa o verde
    # ==================================[lógica verde]==================================
    if (sensor_direito.compare_rgb(verde, limiar_verde)) or (sensor_esquerdo.compare_rgb(verde, limiar_verde)):

        base.straight(5)

        # armazena os valores da leitura do verde depois de uma mini reta
        verde_direita = sensor_direito.compare_rgb(verde, limiar_verde)
        verde_esquerda = sensor_esquerdo.compare_rgb(verde, limiar_verde)

        # anda até sair do verde
        while (sensor_direito.compare_rgb(verde, limiar_verde)) or (sensor_esquerdo.compare_rgb(verde, limiar_verde)):
            base.drive(velocidade_reta + 109, 0)

        # anda um pouco mais do que o verde
        base.straight(6)

        # executa se depois do verde tem preto
        if (sensor_esquerdo.rgb()[1] < limiar_preto + margem_cinza or sensor_direito.rgb()[
            1] < limiar_preto + margem_cinza):
            print("verde")
            if verde_direita and verde_esquerda:
                # 180 graus
                base.straight(40)
                base.curve(150, 0, 90)

                base.drive(0, 90)

                while sensor_esquerdo.rgb()[1] > limiar_preto:
                    wait(1)

                base.brake()

                base.drive(0, -90)

                while sensor_esquerdo.rgb()[1] < limiar_preto + margem_cinza:
                    wait(1)

                base.curve(-3, 0, velocidade_fina)


            else:
                # direita ou esquerda
                sensor_da_curva = sensores.get_sensor_right_if_true(verde_direita)
                sensor_oposto_da_curva = sensores.get_sensor_right_if_true(verde_esquerda)
                curve_sign = (1 if verde_direita else -1)
                starting_angle = hub.imu.heading()

                base.straight(70)
                base.curve(60 * curve_sign, 0, 90)

                base.drive(0, 90 * curve_sign)

                while sensor_oposto_da_curva.rgb()[1] > limiar_preto:
                    wait(1)

                base.brake()

                base.drive(0, -90 * curve_sign)

                while sensor_oposto_da_curva.rgb()[1] < limiar_preto + margem_cinza:
                    wait(1)

                base.curve(-3 * curve_sign, 0, velocidade_fina)

    # ==================================[fim lógica verde]==================================

    # após verde executa o seguidor de linha
    # ==================================[seguidor]==================================
    # Usa o canal VERDE (G) da leitura RGB dos sensores para calcular o erro
    erro_anterior = erro
    erro = sensores.g_difference()

    erro_quadratico = sensores.g_squared_difference()

    derivada = (erro_anterior - erro) / delta_t
    correcao = erro * kp + derivada * kd

    if correcao != 0:
        sinal_correcao = correcao / abs(correcao)
    else:
        sinal_correcao = 0

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

    # - - - - - - - - - - - [Aqui lógica da busca de linha] - - - - - - - - - - -
    if abs(erro_quadratico) > limite_busca and fazer_busca:
        if not estava_na_linha:
            cronometro_linha.reset()
            cronometro_linha.resume()
            angulo_inicio_linha = hub.imu.heading()
            primeiro_erro_linha = erro
        else:
            if cronometro_linha.time() > 2:
                base.straight(7)

                erro_quadratico = sensores.g_squared_difference()

                # verifica se o erro é significativo depois de andar 5 milimetros e se não é verde
                if abs(erro_quadratico) > limite_busca and not ((sensor_direito.compare_rgb(verde, limiar_verde)) or (
                sensor_esquerdo.compare_rgb(verde, limiar_verde))):

                    buscar_para_direita = primeiro_erro_linha < 0

                    base.straight(63)
                    base.curve(30 * (1 if buscar_para_direita else -1), 0, 20)

                    base.drive(0, -1 * velocidade_busca * (1 if buscar_para_direita else -1))

                    while sensores.get_sensor_right_if_true(buscar_para_direita).rgb()[1] > limiar_preto:
                        wait(1)

                    base.brake()

                    base.drive(0, velocidade_reta * (1 if buscar_para_direita else -1))

                    while sensores.get_sensor_right_if_true(buscar_para_direita).rgb()[1] < limiar_preto + margem_cinza:
                        wait(1)

                    base.curve(6 * (1 if buscar_para_direita else -1), 0, velocidade_fina)

        estava_na_linha = True
    else:
        if estava_na_linha:
            tempo_em_linha = cronometro_linha.time()
            cronometro_linha.pause()
        estava_na_linha = False

    # ==================================[fim seguidor]==================================

    wait(1)
