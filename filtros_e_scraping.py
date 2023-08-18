import pandas as pd
# import random
import unicodedata
import re

def remove_acentos(string):

    normalized = unicodedata.normalize('NFD', string)
    return re.sub(r'[\u0300-\u036f]', '', normalized).casefold()

def carrega_dataframe_csv(caminho):
    return pd.read_csv(caminho)


def sorteia_palavra_2(lista_palavra):
    if len(lista_palavra) == 1:
        return lista_palavra[0]
    else:
        return lista_palavra[random.randint(0,(len(lista_palavra)-1))]



def sorteia_palavra(df):
    if len(df) == 1:
        return df.palavra.values.tolist()[0]
    else:
        mask_letras_diferentes = df.n_letras_diferentes == max(df.n_letras_diferentes)
        df = df[mask_letras_diferentes]
        mask_consoantes = df.consoantes_unicas == max(df.consoantes_unicas)
        df = df[mask_consoantes]
        return df.palavra[df.probabilidade == max(df.probabilidade)].values.tolist()[0]

def letra_na_posicao(lista_letra_correta, df):
    if len(lista_letra_correta) == 0:
        return df
    else:
        for letra, posicao in lista_letra_correta:
            if posicao == 0:
                mask = df.letra_0 == letra
                df = df.loc[mask, :]
            elif posicao == 1:
                mask = df.letra_1 == letra
                df = df.loc[mask, :]
            elif posicao == 2:
                mask = df.letra_2 == letra
                df = df.loc[mask, :]
            elif posicao == 3:
                mask = df.letra_3 == letra
                df = df.loc[mask, :]
            elif posicao == 4:
                mask = df.letra_4 == letra
                df = df.loc[mask, :]

    return df


from collections import OrderedDict


# https://www.tutorialspoint.com/program-to-remove-duplicate-characters-from-a-given-string-in-python
def tira_duplicadas_palavra(s):  # removendo as duplicadas da string
    d = OrderedDict()
    for c in s:
        if c not in d:
            d[c] = 0
        d[c] += 1

    return ''.join(d.keys())


def confere_letras_nas_palavras(palavra, letras_desejadas):
    # aqui uma simples checagem se as cada letra da palavra está em letras desejadas (letras)
    contador = 0
    reduzido = tira_duplicadas_palavra(palavra)

    for letra in tira_duplicadas_palavra(palavra):
        if (letra in letras_desejadas):  # condicional para que se tiver na palavra some 1 ao contador
            contador += 1

    #     'pavor' = tira_duplicadas => 'pavor'
    #     'aro' = tira duplicadas => 'aro'
    #     len(aro) = 3
    #     contador = 3

    if (contador == len(tira_duplicadas_palavra(letras_desejadas))):
        # se for verdadeiro o tamanho das letras_desejadas com o numero do contador

        return True
    else:
        return False


def palavras_com_letra_posicao_errada(lista_de_letras_com_posicao, df):
    letras = ''
    for letra, posicao in lista_de_letras_com_posicao:
        letras += letra

        if posicao == 0:
            mask = (df.letra_0 != letra)
            df = df.loc[mask, :]
        elif posicao == 1:
            mask = (df.letra_1 != letra)
            df = df.loc[mask, :]
        elif posicao == 2:
            mask = (df.letra_2 != letra)
            df = df.loc[mask, :]
        elif posicao == 3:
            mask = (df.letra_3 != letra)
            df = df.loc[mask, :]
        elif posicao == 4:
            mask = (df.letra_4 != letra)
            df = df.loc[mask, :]

    return df[df.palavra.apply(lambda x: confere_letras_nas_palavras(x, letras))]


def letras_nao_aceitas(letras, df, letras_aceitas):
    lista = []

    for letra, indice, status_letras_aceitas in letras:
        if status_letras_aceitas == False:
            lista.append(letra)
        else:
            mask = df[f'letra_{indice}'] != letra
            df = df.loc[mask, :]

        if len(lista) > 0:
            mask = ~df.letra_0.isin(lista) & ~df.letra_1.isin(lista) & ~df.letra_2.isin(lista) & ~df.letra_3.isin(
                lista) & ~df.letra_4.isin(lista)
            df = df.loc[mask, :]

    return df


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service

from datetime import datetime
import random

#com a mudança pro selenium 4.0, algumas coisas mudaram ao inicializar, por exemplo o uso do Service

# inicializand o site

def inicializa_termo():
    service = Service(executable_path='./edg_drv/msedgedriver.exe')  # mudança do selenium 4.0
    driver = webdriver.Edge(service=service)

    urlpage = 'https://term.ooo/'
    response = driver.get(urlpage)
    driver.implicitly_wait(5)

    x_path = '/html/body/wc-modal'
    ajuda_sempre_aberta = driver.find_element('xpath', x_path)
    ajuda_sempre_aberta.click()
    driver.implicitly_wait(5)
    return driver


# envia palavra
from time import sleep


def envia_palavra(palavra_sorteada, driver):
    x_path_board = '/html/body'
    board_inicial = driver.find_element('xpath', x_path_board)
    for letra in palavra_sorteada:
        board_inicial.send_keys(letra)
        # board_inicial.implicitly_wait(3)#testar, se não funcionar voltar para -> driver.implicitly_wait(0.5)
        sleep(1)

    board_inicial.send_keys(Keys.ENTER)
    # board_inicial.implicitly_wait(5)
    sleep(3)
    # print('palavra-enviada')#apenas pra finalidades de teste, retirar depois


def apaga_palavra(driver):
    x_path_board = '/html/body'
    board_inicial = driver.find_element('xpath', x_path_board)

    for i in range(5):
        board_inicial.send_keys(Keys.BACKSPACE)
        sleep(0.5)


def retorna_dicionario_respostas(variavel, driver):  # variavel = numero da tentativa

    elemento_do_board = '[id="board0"]'

    shadow = driver.find_element(By.CSS_SELECTOR, elemento_do_board).shadow_root
    letra = ''
    resposta = ''

    lista_da_palavra = []  # inicializa a lista
    elemento_primeira_linha_interno_para_shadow = f'[aria-label="palavra {variavel}"]'
    inner_shadow = shadow.find_element(By.CSS_SELECTOR, elemento_primeira_linha_interno_para_shadow).shadow_root

    for variavel in range(5):
        elemento_primeira_letra = f'[termo-pos="{str(variavel)}"]'
        elemento_html = inner_shadow.find_element(By.CSS_SELECTOR, elemento_primeira_letra)
        resposta = elemento_html.get_attribute('class')
        letra = remove_acentos(elemento_html.text.lower())
        if resposta != 'letter empty':
            lista_da_palavra.append((resposta, letra))

    return dict(zip(range(len(lista_da_palavra)), lista_da_palavra))


def descompacta_dicionario(dicionario, letras_aceitas):
    letras_erradas = []
    letras_lugar_errado = []
    letras_corretas = []

    # primeiro sempre adicionando as letras corretas!
    for item in dicionario:
        letra = remove_acentos(dicionario[item][1]).lower()
        condicao = letra in letras_aceitas
        if dicionario[item][0] == 'letter right':
            letras_aceitas += letra
            letras_corretas.append((dicionario[item][1], item))

    # adicionando as letras corretas mas em posição errada!
    for item in dicionario:
        letra = remove_acentos(dicionario[item][1]).lower()
        condicao = letra in letras_aceitas
        if dicionario[item][0] == 'letter place':
            letras_aceitas += letra
            letras_lugar_errado.append((dicionario[item][1], item))

    # e só por fim adicionar as letras erradas a equação
    for item in dicionario:
        letra = remove_acentos(dicionario[item][1]).lower()
        condicao = letra in letras_aceitas
        if dicionario[item][0] == 'letter wrong':
            if dicionario[item][1] in letras_aceitas:
                letras_erradas.append((dicionario[item][1], item, True))
                # retornando true se a letra errada está na lista de letras aceitas
            else:
                letras_erradas.append((dicionario[item][1], item, False))
                # retornando false se a letra errada está na lista de letras aceitas
    # será necessário criar uma condição só pra letra não aceita + letra aceita por causa do erro do site!

    return letras_erradas, letras_lugar_errado, letras_corretas, letras_aceitas


def filtra_df_2(dicionario, df, letras_aceitas):
    #         envia_palavra(palavra_sorteada)

    #         #pegar informações da palavra enviada
    #         dicionario = retorna_dicionario_respostas(tentativa)

    # retornar resultado das letras
    letras_erradas, letras_lugar_errado, letras_corretas, letras_aceitas = descompacta_dicionario(dicionario,
                                                                                                  letras_aceitas)

    df = letras_nao_aceitas(letras_erradas, df, letras_aceitas)
    df = palavras_com_letra_posicao_errada(letras_lugar_errado, df)
    df = letra_na_posicao(letras_corretas, df)

    return df, letras_aceitas, letras_erradas, letras_lugar_errado, letras_corretas


def filtra_df(dicionario, df, letras_aceitas):
    #         envia_palavra(palavra_sorteada)

    #         #pegar informações da palavra enviada
    #         dicionario = retorna_dicionario_respostas(tentativa)

    # retornar resultado das letras
    letras_erradas, letras_lugar_errado, letras_corretas, letras_aceitas = descompacta_dicionario(dicionario,
                                                                                                  letras_aceitas)

    df = palavras_com_letra_posicao_errada(letras_lugar_errado, df)
    df = letra_na_posicao(letras_corretas, df)
    df = letras_nao_aceitas(letras_erradas, df, letras_aceitas)

    return df, letras_aceitas
# essa função pega a notificação que aparece no site, enquanto não aparecer notificação o jogo não terminou
# ela é recursiva, pois chama ela mesmo quando mandamos uma palavra não aceita pelo site
# o conjunto de palavras ainda está sendo filtrado para sabermos futuramente todas as palavras que o site aceita!
# e algumas foram geradas erroneamente ao limparmos acentos delas
def get_notificacao(palavra_sorteada, df, file, now, session_id, dicionario, tentativa, letras_aceitas, driver):
    # def get_notificacao(palavra_sorteada, df):
    vencedor = 'wc-notify'
    notificacao = driver.find_element(By.CSS_SELECTOR, vencedor)
    notificacao = notificacao.text
    # print(notificacao)
    terminou = True
    if notificacao == '':
        notificacao = 'palavra aceita'  # para input do resultados.txt
        terminou = True


    elif notificacao == 'essa palavra não é aceita':
        #terminou = False
        #file.write(f'{-1},{palavra_sorteada},{notificacao},,{session_id},,{dicionario}\n')
        # nesse ponto precisei meio que criar ela recursivamente, pra ir filtrando as palavras que não poderiamos colocar!
        while notificacao == 'essa palavra não é aceita':#terminou == False:
            # apagando palavra
            apaga_palavra(driver)

            file.write(f'{-1},{palavra_sorteada},{notificacao},,{session_id},,{dicionario}\n')
            # aqui vai ter uma mini função, que talvez eu encapsule em outro lugar
            df = df[df.palavra != palavra_sorteada].reset_index(drop=True)
            palavra_sorteada = sorteia_palavra(df)
            #palavra_sorteada = sorteia_palavra(df.palavra.values.tolist())


            envia_palavra(palavra_sorteada, driver)

            # pegar informações da palavra enviada
            dicionario = retorna_dicionario_respostas(tentativa, driver)

            df, letras_aceitas, letras_erradas, letras_lugar_errado, letras_corretas = filtra_df_2(dicionario, df,
                                                                                                   letras_aceitas)

            # driver.implicitly_wait(10)
            sleep(1)
            print('----------------dentro_get_notificacao--------------------')
            print('palavra sorteada: ', palavra_sorteada)
            print(dicionario)
            print('tentativa: ', tentativa)
            print('letras erradas: ', letras_erradas)
            print('letras lugar errado: ', letras_lugar_errado)
            print('letras corretas: ', letras_corretas)
            print('letras aceitas: ', letras_aceitas)

            # terminou, df, notificacao, palavra_sorteada = get_notificacao(palavra_sorteada, df, file, now, session_id,dicionario,tentativa, letras_aceitas)
            terminou, df, notificacao, palavra_sorteada, letras_aceitas, tentativa = get_notificacao(palavra_sorteada,
                                                                                                     df, file, now,
                                                                                                     session_id,
                                                                                                     dicionario,
                                                                                                     tentativa,
                                                                                                     letras_aceitas,
                                                                                                     driver)
            # tentativa += 1 # foi o jeito de corrigir o erro, não sei como só isso resolveu, verificar deep dps




    else:
        terminou = False

    return terminou, df, notificacao, palavra_sorteada, letras_aceitas, tentativa


def first_attempt():
    return 'aureo'

def second_attempt():
    return 'clips'

def roda_tudo(driver, df, letras_aceitas):
    file = open('resultados.txt', 'a')
    terminou = True
    tentativa = 0

    now = datetime.now()
    data = now.strftime("%d/%m/%Y")
    session_id = driver.session_id

    # só verificando o seed que foi gerado pra caso precisar replicar
    variavel_randomica = random.randint(0, 1000)
    a = random.seed(variavel_randomica)
    print(variavel_randomica)

    # print('first')
    # pegando a primeira palavra
    palavra_sorteada = first_attempt()

    envia_palavra(palavra_sorteada, driver)

    # pegar informações da palavra enviada
    dicionario = retorna_dicionario_respostas(tentativa, driver)

    # print(palavra_sorteada)
    # df, letras_aceitas = filtra_df(dicionario, df, letras_aceitas)

    df, letras_aceitas, letras_erradas, letras_lugar_errado, letras_corretas = filtra_df_2(dicionario, df,
                                                                                           letras_aceitas)

    # driver.implicitly_wait(10)
    sleep(1)
    print('------------------------------------')
    print('palavra sorteada: ', palavra_sorteada)
    print(dicionario)
    print('tentativa: ', tentativa)
    print('letras erradas: ', letras_erradas)
    print('letras lugar errado: ', letras_lugar_errado)
    print('letras corretas: ', letras_corretas)
    print('letras aceitas: ', letras_aceitas)
    #df.to_csv('debugando.csv')

    terminou, df, notificacao, palavra_sorteada, letras_aceitas, tentativa = get_notificacao(palavra_sorteada, df,
                                                                                             file, now, session_id,
                                                                                             dicionario, tentativa,
                                                                                             letras_aceitas, driver)
    tentativa += 1


    #teste de segunda tentativa

    palavra_sorteada = second_attempt()

    envia_palavra(palavra_sorteada, driver)

    # pegar informações da palavra enviada
    dicionario = retorna_dicionario_respostas(tentativa, driver)


    df, letras_aceitas, letras_erradas, letras_lugar_errado, letras_corretas = filtra_df_2(dicionario, df,
                                                                                           letras_aceitas)

    # driver.implicitly_wait(10)
    sleep(1)
    print('------------------------------------')
    print('palavra sorteada: ', palavra_sorteada)
    print(dicionario)
    print('tentativa: ', tentativa)
    print('letras erradas: ', letras_erradas)
    print('letras lugar errado: ', letras_lugar_errado)
    print('letras corretas: ', letras_corretas)
    print('letras aceitas: ', letras_aceitas)

    tentativa += 1

    while terminou == True:
        # driver.implicitly_wait(5)
        # for tentativa in range(5):
        # print(tentativa)



        palavra_sorteada = sorteia_palavra(df)
        #palavra_sorteada = sorteia_palavra(df.palavra.values.tolist())
        # print(palavra_sorteada)

        envia_palavra(palavra_sorteada, driver)

        # pegar informações da palavra enviada
        dicionario = retorna_dicionario_respostas(tentativa, driver)

        # print(palavra_sorteada)
        # df.to_csv('debugando.csv')
        df, letras_aceitas, letras_erradas, letras_lugar_errado, letras_corretas = filtra_df_2(dicionario, df,
                                                                                               letras_aceitas)
        # driver.implicitly_wait(30)
        sleep(1)

        # terminou, df, notificacao, palavra_sorteada, letras_aceitas, tentativa = get_notificacao(palavra_sorteada, df, file, now, session_id, dicionario,tentativa, letras_aceitas)
        print('------------------------------------')
        print('palavra sorteada: ', palavra_sorteada)
        print(dicionario)

        print('tentativa: ', tentativa)
        print('letras erradas: ', letras_erradas)
        print('letras lugar errado: ', letras_lugar_errado)
        print('letras corretas: ', letras_corretas)

        print('letras aceitas: ', letras_aceitas)
        terminou, df, notificacao, palavra_sorteada, letras_aceitas, tentativa = get_notificacao(palavra_sorteada, df,
                                                                                                 file, now, session_id,
                                                                                                 dicionario, tentativa,
                                                                                                 letras_aceitas, driver)

        # file.write('tentativa,palavra,resultado,data,session_id\n')
        file.write(
            f'{tentativa},{palavra_sorteada},{notificacao},{data},{session_id},{variavel_randomica},{dicionario}\n')
        tentativa += 1

        if tentativa > 6:
            terminou = False

    file.close()
