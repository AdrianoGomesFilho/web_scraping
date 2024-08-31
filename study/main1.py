import asyncio  # Permite executar tarefas assíncronas
from pyppeteer import launch  # Permite executar o Chromium headless
from urllib.parse import urlencode  # Permite escapar caracteres especiais
from parametros import nome_advogado, data_inicial, data_final
import json  # Importa JSON para converter dicionários em strings formatadas

# Função criadora do URL
def criar_url(nome_advogado, data_inicial, data_final):
    url_base = "https://comunica.pje.jus.br/consulta"
    parametros = {
        'dataDisponibilizacaoInicio': data_inicial,
        'dataDisponibilizacaoFim': data_final,
        'nomeAdvogado': nome_advogado
    }
    return f"{url_base}?{urlencode(parametros)}"  # Fusão dos parâmetros, adaptado para uma URL

async def abre_pagina_e_coleta_conteudo(url):
    navegador = await launch()  # Inicia o navegador headless
    pagina = await navegador.newPage()  # Abre uma aba
    conteudo_total = []  # Lista para armazenar conteúdo coletado

    try:
        await pagina.goto(url, {'waitUntil': 'networkidle2'})  # Vai para a URL e garante que a página esteja carregada
        
        while True:
            try:
                await pagina.waitForSelector('.numero-unico-formatado', {'timeout': 30000})

                # Avalia o conteúdo dos processos
                processos = await pagina.evaluate('''() => {
                    const processos = [];
                    const numeros = Array.from(document.querySelectorAll('.numero-unico-formatado'));
                    const orgaos = Array.from(document.querySelectorAll('.info-summary'));
                    const intimacoes = Array.from(document.querySelectorAll('.tab_panel2'));
                    
                    for (let i = 0; i < numeros.length; i++) {
                        processos.push({
                            numero_processo: numeros[i]?.innerText,
                            orgao: orgaos[i]?.innerText,
                            conteudo_intimacao: intimacoes[i]?.innerText
                        });
                    }
                    return processos;
                }''')

                conteudo_total.extend(processos)
            
            except Exception as erro_detalhe:
                print(f"Erro de coleta: {erro_detalhe}")
            
            try:
                # Busca os botões dos tribunais e coleta conteúdo
                botoes_tribunais = await pagina.querySelectorAll('.mat-tab-label-content')
                for botao in botoes_tribunais:
                    await botao.click()
                    await pagina.waitForSelector('.numero-unico-formatado', {'visible': True})

                    conteudo_tab_tribunais = await pagina.evaluate('''() => {
                        const processos = [];
                        const numeros = Array.from(document.querySelectorAll('.numero-unico-formatado'));
                        const orgaos = Array.from(document.querySelectorAll('.info-summary'));
                        const intimacoes = Array.from(document.querySelectorAll('.tab_panel2'));
                        
                        for (let i = 0; i < numeros.length; i++) {
                            processos.push({
                                numero_processo: numeros[i]?.innerText,
                                orgao: orgaos[i]?.innerText,
                                conteudo_intimacao: intimacoes[i]?.innerText
                            });
                        }
                        return processos;
                    }''')

                    conteudo_total.extend(conteudo_tab_tribunais)

            except Exception as erro:
                print(f"Erro em selecionar tribunais: {erro}")
            
            try:
                # Verifica se há botão de próxima página disponível (seta) sem status "disable" (cinza), caso contrário, sai do loop
                botao_proxima_pagina = await pagina.querySelector('.ui-paginator-next:not(.ui-state-disabled)')
                if botao_proxima_pagina:
                    await botao_proxima_pagina.click()
                    await pagina.waitFor(2000)  # Aguarda um pouco para carregar
                    await pagina.waitForSelector('.numero-unico-formatado', {'visible': True, 'timeout': 30000})
                else:
                    break  # Quando esgotarem as páginas, finaliza e o while coleta o conteúdo final
            except Exception as erro:
                print(f"Erro ao passar de página: {erro}")
                break

    except Exception as erro:
        print(f"Erro geral: {erro}")
    finally:
        await navegador.close()  # Fecha o navegador para poupar recursos

    if conteudo_total:
        # Converte cada dicionário em JSON formatado e une-os com duas novas linhas entre eles
        return "\n\n".join(json.dumps(processo, ensure_ascii=False, indent=2) for processo in conteudo_total)
    else:
        return "Não há conteúdo encontrado"

async def funcao_principal():
    url_final = criar_url(nome_advogado, data_inicial, data_final)
    conteudo = await abre_pagina_e_coleta_conteudo(url_final)
    print("Nome do advogado buscado:", nome_advogado)
    print("Datas buscadas:", data_inicial, data_final)
    print("Conteúdo:", conteudo)

# Verifica e cria um novo loop de eventos se não existir um
if __name__ == "__main__":
    asyncio.run(funcao_principal())
