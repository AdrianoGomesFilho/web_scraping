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

async def abrir_página_e_coleta_conteúdo(url):
    browser = await launch()
    page = await browser.newPage()
    all_content = set()

    try:
        await page.goto(url, {'waitUntil': 'networkidle2'})

        while True:
            # Coleta o conteúdo da aba inicial na página atual
            try:
                await page.waitForSelector('.numero-unico-formatado', {'timeout': 30000})
                initial_content_texts = await page.evaluate('''() => { 
                    return Array.from(document.querySelectorAll('.numero-unico-formatado')).map(element => element.innerText);
                }''')
                all_content.update(initial_content_texts)
            except Exception as e:
                print(f"Erro ao coletar conteúdo inicial: {e}")

            # Encontra todos os botões para as outras abas
            try:
                tab_buttons = await page.querySelectorAll('.mat-tab-label-content')
                for button in tab_buttons:
                    await button.click()
                    await page.waitForSelector('.numero-unico-formatado', {'visible': True})
                    
                    tab_content_texts = await page.evaluate('''() => {
                        return Array.from(document.querySelectorAll('.numero-unico-formatado')).map(element => element.innerText); 
                    }''')
                    
                    all_content.update(tab_content_texts)
            except Exception as e:
                print(f"Erro ao clicar nas abas: {e}")

            # Verifica se há um próximo botão de página e clica nele, caso contrário sai do loop
            try:
                next_button = await page.querySelector('.ui-paginator-next:not(.ui-state-disabled)')
                if next_button:
                    await next_button.click()
                    await page.waitFor(2000)  # Wait briefly for the page to load
                    await page.waitForSelector('.numero-unico-formatado', {'visible': True, 'timeout': 30000})
                    print("Navegando para a próxima página...")
                else:
                    break
            except Exception as e:
                print(f"Erro ao navegar para a próxima página: {e}")
                break

    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        await browser.close()
    
    if all_content:
        return "\n\n".join(all_content)
    else:
        return "Conteúdo da classe 'numero-unico-formatado' não encontrado"

async def main():
    url = create_url(name, start_date, end_date)
    print("URL Gerada:", url)
    content = await abrir_página_e_coleta_conteúdo(url)
    print("Conteúdo das abas:", content)

asyncio.get_event_loop().run_until_complete(main())
