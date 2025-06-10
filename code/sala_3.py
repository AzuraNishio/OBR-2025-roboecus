from setup import *
from constantes import *
from pybricks.tools import wait
from utils import sair_sala_3_reto, quantizar_angulo

def verificar_sala3():
    if sensor_direito.reflection() > 80:

        cronometro.reset()

        while cronometro.time() < 3000: #alinhar na fita prata
            f = sensor_esquerdo.reflection() + sensor_direito.reflection()

            f = 180 - f

            c = sensores.reflection_difference() * -1
            base.drive(f, c)


        print("[Sala 3] Condição inicial satisfeita, reflexo do sensor direito:", sensor_direito.reflection())
        lado_do_sensor = 1
        entrada_meio = False
        lado_oposto_do_sensor = -lado_do_sensor
        u = 330  # 1 terço da sala 3 em milímetros
        sonic_limit = pow(2, 0.5) * 3 * u

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

            if not (dist1 > u and dist1 < 2 * u):
                base.curve(lado_do_sensor * -90, 0, velocidade_fina)
                base.straight(dist1 - (u * 1.5) + 80)


            if dist1 > u * 1.7 and sonic.distance() > sonic_limit:
                print("[Sala 3] Nova condição satisfeita, saindo reto")
                base.curve(lado_do_sensor * -90, 0, velocidade_fina)
                sair_sala_3_reto(hub, base, sensores, False, u)
            else:
                print("[Sala 3] Curvando para o lado oposto")

                if dist1 > u and dist1 < 2 * u:
                    dist2 = u
                else:
                    dist2 = sonic.distance()
                    base.curve(lado_do_sensor * 90, 0, velocidade_fina)

                if dist2 < u:
                    base.straight(-u)

                base.drive(70, 0)

                while sensor_frente.reflection() < 40 and sonic.distance() < sonic_limit:
                    wait(1)

                base.brake()
                print("[Sala 3] Checando distância frontal")

                if sonic.distance() > sonic_limit:
                    print("[Sala 3] saindo da sala 3")
                    base.straight(u - 200)
                    base.curve(lado_do_sensor * -90, 0, velocidade_fina)

                    sair_sala_3_reto(hub, base, sensores, False, u)
                else:
                    print("[Sala 3] virando para testar parede oposta")
                    base.curve(lado_do_sensor * 180, 0, velocidade_fina)
                    base.straight(-0.5 * u)
                    base.drive(50, 0)

                    while sensor_frente.reflection() < 40 and sonic.distance() < sonic_limit:
                        wait(1)

                    base.brake()

                    if sonic.distance() > sonic_limit:
                        print("[Sala 3] saindo da sala 3")
                        base.straight(u - 200)
                        base.curve(lado_do_sensor * -90, 0, velocidade_fina)
                        sair_sala_3_reto(hub, base, sensores, False, u)
                    else:
                        print("[Sala 3] testando paredes restantes")
                        base.straight(u*0.5)
                        base.straight(-u * 1.5 + 00)
                        base.curve(-90,0,velocidade_fina)

                        base.drive(70, 0)

                        while sensor_frente.reflection() < 40 and sonic.distance() < sonic_limit:
                            wait(1)

                        base.brake()
                        print("[Sala 3] Checando distância frontal")

                        if sonic.distance() > sonic_limit:
                            print("[Sala 3] saindo da sala 3")
                            base.straight(u - 200)
                            base.curve(lado_do_sensor * -90, 0, velocidade_fina)

                            sair_sala_3_reto(hub, base, sensores, False, u)

                        else:
                            base.curve(180, 0, velocidade_fina)
                            base.drive(-0.5 * u)
                            base.drive(70, 0)

                            while sensor_frente.reflection() < 40 and sonic.distance() < sonic_limit:
                                wait(1)

                            base.brake()
                            print("[Sala 3] Checando distância frontal")

                            if sonic.distance() > sonic_limit:
                                print("[Sala 3] saindo da sala 3")
                                base.straight(u - 200)
                                base.curve(lado_do_sensor * -90, 0, velocidade_fina)

                                sair_sala_3_reto(hub, base, sensores, False, u)

                            else:
                                base.curve(180, 0, velocidade_fina)
                                base.drive(-0.5 * u)
                                base.drive(70, 0)

                                while sensor_frente.reflection() < 40 and sonic.distance() < sonic_limit:
                                    wait(1)

                                base.brake()
                                print("[Sala 3] Checando distância frontal")

                                if sonic.distance() > sonic_limit:
                                    print("[Sala 3] saindo da sala 3")
                                    base.straight(u - 200)
                                    base.curve(lado_do_sensor * -90, 0, velocidade_fina)

                                    sair_sala_3_reto(hub, base, sensores, False, u)



