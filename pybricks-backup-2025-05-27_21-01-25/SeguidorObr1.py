# Importando as bibliotecas necessárias do Pybricks
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Direction, Port
from pybricks.tools import wait, StopWatch
from ReLib import ReDriveBase, ReColor  # Biblioteca personalizada com recursos de movimentação

# Inicializa o hub e os cronômetros
hub = PrimeHub()
cronometro = StopWatch()
cronometro_linha = StopWatch()

# Sensores de cor
sensor_direito = ReColor(Port.B)
sensor_esquerdo = ReColor(Port.A)

# Motores
motor_esquerdo = Motor(Port.E)
motor_direito = Motor(Port.F, Direction.COUNTERCLOCKWISE)

# Base de movimentação personalizada
base = ReDriveBase(motor_esquerdo, motor_direito, wheel_diameter=38, axle_track=112)

# Parâmetros PIC
kp = -8
kd = 0.012
kc = 0.06

# Velocidades
velocidade_base = 75
velocidade_reta = 120
velocidade_busca = 100
velocidade_fina = 10
fazer_busca = True

# Limiares
limite_busca = 49
limiar_preto = 10
margem_cinza = 12

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

# Loop principal
while True:
    tempo_atual = cronometro.time()
    delta_t = max(0.001, (tempo_atual - ultimo_tempo) / 1000)
    ultimo_tempo = tempo_atual

    # Usa o canal VERDE (G) da leitura RGB dos sensores
    erro_anterior = erro
    erro = sensor_direito.rgb()[1] - sensor_esquerdo.rgb()[1]

    erro_quadratico = pow(
        pow(sensor_direito.rgb()[1], 2) - pow(sensor_esquerdo.rgb()[1], 2), 0.5
    )

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

    if abs(erro_quadratico) > limite_busca and fazer_busca:
        if not estava_na_linha:
            cronometro_linha.reset()
            cronometro_linha.resume()
            angulo_inicio_linha = hub.imu.heading()
            primeiro_erro_linha = erro
        else:
            if cronometro_linha.time() > 2:
                base.straight(5)
                erro_quadratico = pow(
                    pow(sensor_direito.rgb()[1], 2) - pow(sensor_esquerdo.rgb()[1], 2), 0.5
                )
                if abs(erro_quadratico) > limite_busca:
                    base.straight(65)
                    base.curve(30 * (primeiro_erro_linha / abs(primeiro_erro_linha)), 0, 20)

                    base.drive(0, -1 * velocidade_busca * (primeiro_erro_linha / abs(primeiro_erro_linha)))

                    if primeiro_erro_linha < 0:
                        while sensor_esquerdo.rgb()[1] > limiar_preto:
                            wait(1)
                    else:
                        while sensor_direito.rgb()[1] > limiar_preto:
                            wait(1)

                    base\.brake()

                    base.drive(0, velocidade_reta * (primeiro_erro_linha / abs(primeiro_erro_linha)))

                    if primeiro_erro_linha < 0:
                        while sensor_esquerdo.rgb()[1] < limiar_preto + margem_cinza:
                            wait(1)
                    else:
                        while sensor_direito.rgb()[1] < limiar_preto + margem_cinza:
                            wait(1)

        estava_na_linha = True
    else:
        if estava_na_linha:
            tempo_em_linha = cronometro_linha.time()
            cronometro_linha.pause()
        estava_na_linha = False

    wait(1)
