import asyncio #permite executar tarefas assíncronas
from pyppeteer import launch #permite executar o chromium headless
from urllib.parse import urlencode #permite escapar caracteres especiais
from parametros import nome_advogado, data_inicial, data_final

#funcao criadora do URL
def criar_url(nome_advogado, data_inicial, data_final):
    url_base = "https://comunica.pje.jus.br/consulta"
    parametros = {
        'dataDisponibilizacaoInicio': data_inicial,
        'dataDisponibilizacaoFim': data_final,
        'nomeAdvogado': nome_advogado
    }
    return f"{url_base}?{urlencode(parametros)}" #fusao dos parametros, adaptado para uma url

async def abre_pagina_e_coleta_conteudo(url):
    navegador = await launch() #inicia o navegador headless
    pagina = await navegador.newPage() #abre uma aba
    conteudo_total = set() #set = conjunto de dados não repetidos

    try:
        await pagina.goto(url, {'waitUntil': 'networkidle2'})#vai para a URL e garante que esteja carregada a página 
        while True:
            try:
                await pagina.waitForSelector('.numero-unico-formatado', {'timeout':30000})
                numero_processo = await pagina.evaluate('''() => {
                    return Array.from(document.querySelectorAll('.numero-unico-formatado')).map(element => element.innerText);
                    }''') #evaluate é do pyppeteer, permite executar JS na página, aqui vai retornar um array
                
                orgao = await pagina.evaluate('''() => { 
                    return Array.from(document.querySelectorAll('.info-summary')).map(element => element.innerText);
                }''')
                
                conteudo_intimacao = await pagina.evaluate('''() => { 
                    return Array.from(document.querySelectorAll('.tab_panel2')).map(element => element.innerText);
                }''')
                conteudo_total.update({
                    'numero_processo': numero_processo,
                    'orgao': orgao,
                    'conteudo_intimacao': conteudo_intimacao
                })
            except Exception as erro_detalhe:
                print(f"Erro de coleta: {erro_detalhe}")
            
            try: #busca os botoes dos tribunais e coleta conteudo
                botoes_tribunais = await pagina.querySelectorAll('.mat-tab-label-content')
                for botao in botoes_tribunais:
                    await botao.click()
                    await pagina.waitForSelector('.numero-unico-formatado',{'visible': True})

                    conteudo_tab_tribunais = await pagina.evaluate('''() => {return Array.from(document.querySelectorAll('.numero-unico-formatado')).map(element => element.innerText);}''')

                    conteudo_total.update(conteudo_tab_tribunais)
            except Exception as erro:
                print(f"Erro em selecionar tribunais: {erro}")
            
            try: #verifica se tem botao de prox pagina disponivel (seta) sem status "disable" = cinza, caso contrário, sai do loop
                botao_proxima_pagina = await pagina.querySelector('.ui-paginator-next:not(.ui-state-disabled)')
                if botao_proxima_pagina:
                    await  botao_proxima_pagina.click()
                    await pagina.waitFor(2000) #aguarda um pouco para carregar
                    await pagina.waitForSelector('.numero-unico-formatado', {'visible': True, 'timeout':30000})

                else:
                    break #quando esgotarem as paginas, finaliza e o while coleta o conteudo final
            except Exception as erro:
                print(f"Erro ao passar de página: {erro}")
                break

    except Exception as erro:
        print(f"Erro geral: {erro}")
    finally:
        await navegador.close() #fecha o navegador para poupar recursos

    if conteudo_total:
        return "\n\n".join(conteudo_total) #junta os elementos e adiciona uma linha em branco entre eles \n\n
    else:
        return "Não há conteúdo encontrado"
    
async def funcao_principal():
    url_final = criar_url(nome_advogado, data_inicial, data_final)
    # print("URL gerada:", url_final)
    conteudo = await abre_pagina_e_coleta_conteudo(url_final)
    print("Nome do advogado buscado:", nome_advogado)
    print("Datas buscadas:", data_inicial, data_final)
    print("Conteúdo:", conteudo)

#trigger do código
asyncio.get_event_loop().run_until_complete(funcao_principal()) 
                