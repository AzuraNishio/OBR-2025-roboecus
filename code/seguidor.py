from setup import hub, base, sensores, cronometro, cronometro_linha
from constantes import *
from pybricks.tools import wait
from verde import verificar_verde

curva_cumulativa = 0
erro = 0
ultimo_tempo = cronometro.time()
tempo_em_linha = 0
angulo_inicio_linha = 0
primeiro_erro_linha = 0
estava_na_linha = False

def seguir_linha():
    global erro, ultimo_tempo, curva_cumulativa, estava_na_linha, primeiro_erro_linha

    tempo_atual = cronometro.time()
    delta_t = max(0.001, (tempo_atual - ultimo_tempo) / 1000)
    ultimo_tempo = tempo_atual

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

    if abs(erro_quadratico) > limite_busca and fazer_busca:
        print("[Busca] Linha perdida, buscando...")
        if not estava_na_linha:
            cronometro_linha.reset()
            cronometro_linha.resume()
            angulo_inicio_linha = hub.imu.heading()
            primeiro_erro_linha = erro
            print(f"[Busca] Nova busca iniciada. Angulo inicio: {angulo_inicio_linha:.2f}, primeiro erro: {primeiro_erro_linha:.3f}")
        else:
            if cronometro_linha.time() > 2:
                print("[Busca] Tentando encontrar linha após 2 segundos")
                base.straight(7)
                erro_quadratico = sensores.g_squared_difference()
                print(f"[Busca] erro_quadratico após avanço: {erro_quadratico}")

                if abs(erro_quadratico) > limite_busca and not (sensor_direito.compare_rgb(verde, limiar_verde) or sensor_esquerdo.compare_rgb(verde, limiar_verde)):
                    buscar_para_direita = primeiro_erro_linha < 0
                    print(f"[Busca] Buscando para {'direita' if buscar_para_direita else 'esquerda'}")
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
                    print("[Busca] Linha encontrada, manobra de retorno feita")

        estava_na_linha = True
    else:
        if estava_na_linha:
            tempo_em_linha = cronometro_linha.time()
            cronometro_linha.pause()
            print(f"[Busca] Linha encontrada novamente, tempo na linha: {tempo_em_linha} ms")
        estava_na_linha = False


