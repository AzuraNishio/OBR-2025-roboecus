from constantes import *
from setup import *
from pybricks.tools import wait
from pybricks.tools import StopWatch

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

def testar_slope():
    base.drive(70, 0)
    now = sensor_direito.reflection()
    max = 0
    timer = StopWatch()
    timer.reset()

    while timer.time() < 1000:
        delta = now - sensor_direito.reflection()
        now = sensor_direito.reflection()
        max = delta if (max < delta) else max
        #print(delta, "max ", max)

    return max