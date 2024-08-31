import asyncio
from pyppeteer import launch
from urllib.parse import urlencode
from parametros import nome_advogado, data_inicial, data_final
import json

# Function to create the URL
def criar_url(nome_advogado, data_inicial, data_final):
    url_base = "https://comunica.pje.jus.br/consulta"
    parametros = {
        'dataDisponibilizacaoInicio': data_inicial,
        'dataDisponibilizacaoFim': data_final,
        'nomeAdvogado': nome_advogado
    }
    return f"{url_base}?{urlencode(parametros)}"

# Function to open the page and collect content
async def abre_pagina_e_coleta_conteudo(url):
    navegador = await launch()  
    pagina = await navegador.newPage()  
    conteudo_total = []  

    try:
        await pagina.goto(url, {'waitUntil': 'networkidle2'})  
        
        while True:
            try:
                await pagina.waitForSelector('.card.fadeIn', {'timeout': 30000})  

                # Collect all text from the parent element '.card.fadeIn' including all nested elements
                processos = await pagina.evaluate('''() => {
                    const processos = [];
                    const cards = document.querySelectorAll('.card.fadeIn');

                    cards.forEach(card => {
                        processos.push(card.innerText.trim());  // Collects all inner text from the card, including nested elements
                    });

                    return processos;
                }''')

                conteudo_total.extend(processos)
            
            except Exception as erro_detalhe:
                print(f"Erro de coleta: {erro_detalhe}")
            
            try:
                botoes_tribunais = await pagina.querySelectorAll('.mat-tab-label-content')
                for botao in botoes_tribunais:
                    await botao.click()
                    await pagina.waitForSelector('.numero-unico-formatado', {'visible': True})

                    conteudo_tab_tribunais = await pagina.evaluate('''() => {
                        const processos = [];
                        const cards = document.querySelectorAll('.card.fadeIn');

                        cards.forEach(card => {
                            processos.push(card.innerText.trim());  // Collects all inner text from the card, including nested elements
                        });

                        return processos;
                    }''')

                    conteudo_total.extend(conteudo_tab_tribunais)

            except Exception as erro:
                print(f"Erro em selecionar tribunais: {erro}")
            
            try:
                botao_proxima_pagina = await pagina.querySelector('.ui-paginator-next:not(.ui-state-disabled)')
                if botao_proxima_pagina:
                    await botao_proxima_pagina.click()
                    await pagina.waitFor(2000)
                    await pagina.waitForSelector('.numero-unico-formatado', {'visible': True, 'timeout': 30000})
                else:
                    break
            except Exception as erro:
                print(f"Erro ao passar de página: {erro}")
                break

    except Exception as erro:
        print(f"Erro geral: {erro}")
    finally:
        await navegador.close()

    if conteudo_total:
        return "\n\n".join(conteudo_total)  # Join all text content with double newline separator
    else:
        return "Não há conteúdo encontrado"

async def funcao_principal():
    url_final = criar_url(nome_advogado, data_inicial, data_final)
    conteudo = await abre_pagina_e_coleta_conteudo(url_final)
    print("Nome do advogado buscado:", nome_advogado)
    print("Datas buscadas:", data_inicial, data_final)
    print("Conteúdo:", conteudo)

if __name__ == "__main__":
    asyncio.run(funcao_principal())
