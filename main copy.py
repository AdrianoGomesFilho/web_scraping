import asyncio
from pyppeteer import launch
from urllib.parse import urlencode
from nomes_dos_advogados import nome_do_advogado

def create_url(nome_do_advogado):
    base_url = "https://comunica.pje.jus.br/consulta"
    parametros_url = { 
        'nomeAdvogado': nome_do_advogado
    }
    return f"{base_url}?{urlencode(parametros_url)}"

async def abrir_pagina_e_coleta_conteudo(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    
    await page.waitForSelector('.main-panel')

    initial_content_texts = await page.evaluate(
        '''() => {
        return Array.from(document.querySelectorAll('.main-panel')).map(element => element.innerText);
        }''')
    
    tab_buttons = await page.querySelectorAll('.mat-tab-label-content')

    all_content = []

    for i, button in enumerate(tab_buttons):
        await button.click()
        await page.waitForSelector('.main-panel', {'visible': True})

        tab_content_texts = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.main-panel')).map(element => element.innerText);
        }''')

        all_content.extend(tab_content_texts)

    await browser.close()

    if all_content:
        return "\n\n".join(all_content)
    else:
        return "Publicações não encontradas"
    
async def main():
    url = create_url(nome_do_advogado)
    print("URL gerada:", url)
    content = await abrir_pagina_e_coleta_conteudo(url)
    print("Conteúdo das abas:", content)

asyncio.get_event_loop().run_until_complete(main())