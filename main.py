import asyncio
from pyppeteer import launch
from urllib.parse import urlencode

def create_url(name):
    base_url = "https://comunica.pje.jus.br/consulta"
    params = {
        'nomeAdvogado': name
    }
    url = f"{base_url}?{urlencode(params)}"
    return url.replace('+', '%20')  # Substitui + por %20

async def fetch_and_extract_content(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    
    # Aguarda a renderização completa
    await page.waitForSelector('.main-panel')

    # Coleta o conteúdo da aba inicial
    initial_content_texts = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.main-panel')).map(element => element.innerText);
    }''')
    
    # Encontra todos os botões para as outras abas
    tab_buttons = await page.querySelectorAll('.mat-tab-label-content')
    
    all_content = []

    # Itera sobre cada botão de aba, simula um clique e coleta o conteúdo
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
        return "Conteúdo da classe 'main-panel' não encontrado"

async def main():
    # Nome do advogado
    name = "vitor leandro de oliveira"
    
    # Criar URL com o nome do advogado
    url = create_url(name)
    print("URL Gerada:", url)
    content = await fetch_and_extract_content(url)
    print("Conteúdo das abas:", content)

# Executar o main async
asyncio.get_event_loop().run_until_complete(main())
