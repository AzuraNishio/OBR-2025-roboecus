from setup import *
from constantes import *
from pybricks.tools import wait
from utils import sair_sala_3_reto, quantizar_angulo

def verificar_sala3():
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
