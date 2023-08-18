import filtros_e_scraping

letras_aceitas = ''

caminho = 'br-utf8_prob.csv'

df = filtros_e_scraping.carrega_dataframe_csv(caminho)
driver = filtros_e_scraping.inicializa_termo()
filtros_e_scraping.roda_tudo(driver, df, letras_aceitas)

#568 deu 3 tentativas com palavras não aceitas: premo, iremo, prepo
#necessário criar outra forma de escolher palavras
#possivelmente seria melhor se tivesse um seletor de palavras com + consoantes tbm