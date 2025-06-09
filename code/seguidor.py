from setup import hub, base, sensores, cronometro, cronometro_linha, sensor_direito, sensor_esquerdo
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

    if abs(correcao) > 13:
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


    #Código buscar linha
    if sensores.compare_both_to_color(preto, limiar_preto):
        if not estava_na_linha:
            #codigo que executa ao ENTRAR na linha
            cronometro_linha.reset()
            cronometro_linha.resume()
            angulo_inicio_linha = hub.imu.heading()
            primeiro_erro_linha = erro
            print(f"[Busca] Nova entrou na linha. Angulo inicio: {angulo_inicio_linha:.2f}, primeiro erro: {primeiro_erro_linha:.3f}")
        else:
            #codigo que executa ENQUANTO estiver na linha

            if erro > limite_busca:
                if cronometro_linha.time() > 3: #buscar linha se estiver na linha a 3 milissegundos
                    base.straight(7) #avança 7 milimetros para checar se está mesmo em um lugar para buscar a linha
                    erro_quadratico = sensores.g_squared_difference()

                    if abs(erro_quadratico) > limite_busca and not sensores.is_one_sensor_on_color(verde, limiar_confirmacao_verde):
                        #Setup buscar linha
                        buscar_para_direita = primeiro_erro_linha < 0
                        lado = 1 if buscar_para_direita else -1
                        reta = 56
                        curva = 30
                        curva_correcao = 6
                        sensor_do_lado = sensores.get_sensor_right_if_true(buscar_para_direita)

                        # última verificação, uma leve curva
                        base.straight(7)
                        base.curve(-6 * lado, 0, velocidade_fina)
                        if sensor_do_lado.compare_rgb(preto, limiar_preto):
                            base.curve(6 * lado, 0, velocidade_fina)
                            print(f"[Busca] Buscando para {'direita' if buscar_para_direita else 'esquerda'}")
                            base.straight(reta)
                            base.curve(curva * lado, 0, 20)
                            base.drive(0, -1 * velocidade_busca * lado)

                            while not sensor_do_lado.compare_rgb(preto, limiar_preto):
                                wait(1)

                            base.brake()
                            base.drive(0, velocidade_reta * lado)

                            while sensor_do_lado.compare_rgb(preto, limiar_preto):
                                wait(1)

                            base.curve(curva_correcao * lado, 0, velocidade_fina)
                            print("[Busca] Linha encontrada")

        estava_na_linha = True
    else:
        if estava_na_linha:
            print(f"saiu da linha.")
            tempo_em_linha = cronometro_linha.time()
            cronometro_linha.pause()
        estava_na_linha = False


