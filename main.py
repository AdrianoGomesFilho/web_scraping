from requests_html import HTMLSession
from urllib.parse import urlencode

def create_url(name):
    base_url = "https://comunica.pje.jus.br/consulta"
    params = {
        'nomeAdvogado': name
    }
    return f"{base_url}?{urlencode(params)}"

def fetch_and_extract_content(url):
    session = HTMLSession()
    response = session.get(url)
    
    # Executa o JavaScript na página
    response.html.render()
    
    # Encontrar o conteúdo da classe "tab_panel2 ng-star-inserted"
    tab_content = response.html.find('.tab_panel2.ng-star-inserted')
    if tab_content:
        return tab_content[0].text.strip()  # Retorna o texto do primeiro elemento encontrado
    else:
        return "Conteúdo da classe 'tab_panel2 ng-star-inserted' não encontrado"

def main():
    # Nome do advogado
    name = "vitor leandro de oliveira"
    
    # Criar URL com o nome do advogado
    url = create_url(name)
    
    # Fazer a requisição e extrair o conteúdo
    content = fetch_and_extract_content(url)
    print("Conteúdo da classe 'tab_panel2 ng-star-inserted':", content)

if __name__ == "__main__":
    main()
