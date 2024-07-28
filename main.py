from requests_html import HTMLSession
from urllib.parse import urlencode

def create_url(name):
    base_url = "https://comunica.pje.jus.br/consulta"
    params = {
        'nomeAdvogado': name
    }
    url = f"{base_url}?{urlencode(params)}"
    return url.replace('+', '%20')  # Substitui + por %20

def fetch_and_extract_content(url):
    session = HTMLSession()
    response = session.get(url)
    
    if response.status_code != 200:
        return f"Request failed with status code: {response.status_code}"
    
    # Print the raw HTML content before rendering JavaScript
    print("Raw HTML content before rendering JavaScript:")
    print(response.html.html)
    
    # Executa o JavaScript na página com um tempo de espera maior
    response.html.render(sleep=5)  # Aumente o tempo de espera se necessário
    
    # Print the HTML content after rendering JavaScript
    print("HTML content after rendering JavaScript:")
    print(response.html.html)
    
    # Encontrar todos os elementos com a classe "main-panel"
    content_texts = response.html.find('.main-panel')

    print("Elements found:", content_texts)
    
    # Coletar o texto de cada elemento encontrado
    all_content = [content.text.strip() for content in content_texts]
    
    if all_content:
        return "\n\n".join(all_content)  # Junta todo o texto em uma única string, separada por duas quebras de linha
    else:
        return "Conteúdo da classe 'content-texto' não encontrado"

def main():
    # Nome do advogado
    name = "vitor leandro de oliveira"
    
    # Criar URL com o nome do advogado
    url = create_url(name)
    
    # Depurar a URL gerada
    print("URL Gerada:", url)
    
    # Fazer a requisição e extrair o conteúdo
    content = fetch_and_extract_content(url)
    print("Conteúdo das classes 'content-texto':", content)

if __name__ == "__main__":
    main()
