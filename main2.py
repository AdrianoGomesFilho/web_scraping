import asyncio
from pyppeteer import launch
from urllib.parse import urlencode
from parametros import name, start_date, end_date

def create_url(name, start_date, end_date):
    base_url = "https://comunica.pje.jus.br/consulta"
    params = {
        'dataDisponibilizacaoInicio': start_date,
        'dataDisponibilizacaoFim': end_date,
        'nomeAdvogado': name
    }
    return f"{base_url}?{urlencode(params)}"

async def collect_page_data(page):
    # Coleta o conteúdo da página atual
    try:
        content_texts = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.numero-unico-formatado')).map(element => element.innerText);
        }''')
        return content_texts
    except Exception as e:
        print(f"Error collecting page data: {e}")
        return []

async def process_tabs(page):
    all_content = []
    try:
        tab_buttons = await page.querySelectorAll('.mat-tab-label-content')
        
        for button in tab_buttons:
            try:
                await page.waitForSelector('.numero-unico-formatado', {'visible': True})
                await button.click()
                await page.waitForSelector('.numero-unico-formatado', {'visible': True})
                
                tab_content_texts = await collect_page_data(page)
                all_content.extend(tab_content_texts)
            except Exception as e:
                print(f"Error processing tab: {e}")
    
    except Exception as e:
        print(f"Error finding tabs: {e}")

    return all_content

async def abrir_página_e_coleta_conteúdo(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    
    all_content = []

    while True:
        try:
            # Processa as abas da página atual
            page_content_texts = await process_tabs(page)
            all_content.extend(page_content_texts)
            
            # Encontra e processa os botões de próxima página
            next_buttons = await page.querySelectorAll('.ui-paginator-page')
            if not next_buttons:
                break

            for i in range(len(next_buttons)):
                try:
                    await page.waitForSelector('.ui-paginator-page', {'visible': True})
                    await next_buttons[i].click()
                    await page.waitForSelector('.numero-unico-formatado', {'visible': True})
                    
                    # Processa abas após a mudança de página
                    page_content_texts = await process_tabs(page)
                    all_content.extend(page_content_texts)
                    
                except Exception as e:
                    print(f"Error clicking page button or processing page: {e}")
                    break
        
        except Exception as e:
            print(f"Error during pagination: {e}")
            break

    await browser.close()
    
    if all_content:
        return "\n\n".join(all_content)
    else:
        return "Conteúdo da classe 'numero-unico-formatado' não encontrado"

async def main():
    url = create_url(name, start_date, end_date)
    print("URL Gerada:", url)
    content = await abrir_página_e_coleta_conteúdo(url)
    print("Conteúdo das páginas:", content)

asyncio.get_event_loop().run_until_complete(main())
