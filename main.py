import asyncio #bliblioteca que permite executar tarefas assincronas usando o async and await
from pyppeteer import launch #biblioteca que permite executar um chromium headless, launch é para inicializar
from urllib.parse import urlencode #importa alguns parametros capazes de formatar string e escapar caracteres especiais
from nomes_dos_advogados import nome_do_advogado

def create_url(nome_do_advogado):
    base_url = "https://comunica.pje.jus.br/consulta"
    params = {
        'nomeAdvogado': nome_do_advogado
    }
    return f"{base_url}?{urlencode(params)}"

async def abrir_página_e_coleta_conteudo(url):
    browser = await launch() #abre um browser headless (sem interface gráfica)
    page = await browser.newPage() #abre uma aba no browser
    await page.goto(url, {'waitUntil': 'networkidle2'}) #vai para o url criado, esperando até a internet diminuir velocidade (garante que a página deu load completo)
    
    # Aguarda a renderização completa
    await page.waitForSelector('.main-panel')

    # Coleta o conteúdo da aba inicial. Será repetido em outras abas
    # O page.evaluate passa um código em JS, que aparenta ser uma string completa. Os ''' em python permite fazer string multi linhas
    initial_content_texts = await page.evaluate('''() => { 
        return Array.from(document.querySelectorAll('.main-panel')).map(element => element.innerText);
    }''')
    
    # Encontra todos os botões para as outras abas
    tab_buttons = await page.querySelectorAll('.mat-tab-label-content')
    
    all_content = []

    # Itera sobre cada botão de aba, simula um clique e coleta o conteúdo
    for i, button in enumerate(tab_buttons): #o enumerate evita ter que declarar index o e depois somar +1, deixando mais conciso. Ele vai iterar sobre os items o mesmo jeito
        await button.click()
        await page.waitForSelector('.main-panel', {'visible': True})
        
        tab_content_texts = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.main-panel')).map(element => element.innerText); 
        }''') #roda uma função arrow anônima na página, sabemos pelo (), sem parâmetros, que retorna um array com todos os elementos com a classe .main-panel. O .map itera o array, aplicando uma função de arrow que extrai o innerText
        
        all_content.extend(tab_content_texts) #o extend adiciona ao all_content (já declarado antes) que continha os dados iniciais
    
    await browser.close()
    
    if all_content:
        return "\n\n".join(all_content)
    else:
        return "Conteúdo da classe 'main-panel' não encontrado"

async def main():
    
    # Criar URL com o nome do advogado (importado do arquivo externo)
    url = create_url(nome_do_advogado)
    print("URL Gerada:", url)
    content = await abrir_página_e_coleta_conteudo(url)
    print("Conteúdo das abas:", content)

# Executar o main async
asyncio.get_event_loop().run_until_complete(main())
