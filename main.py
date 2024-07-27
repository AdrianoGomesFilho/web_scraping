import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Define the URL and query parameters
url = "https://comunica.pje.jus.br/consulta"
today_date = datetime.today().strftime('%Y-%m-%d')
params = {
    'dataDisponibilizacaoInicio': today_date,
    'dataDisponibilizacaoFim': today_date,
    'nomeAdvogado': 'vitor leandro de oliveira'
}

# Perform the GET request without headers
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the desired element
    numero_unico = soup.find_all(class_='numero-unico-formatado')
    
    # Print the result
    if numero_unico:
        for numero in numero_unico:
            print(numero.text)
    else:
        print("Element not found")
else:
    print(f"Request failed with status code {response.status_code}")
