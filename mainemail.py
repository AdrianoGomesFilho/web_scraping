import asyncio
from pyppeteer import launch
from urllib.parse import urlencode
from email.mime.text import MIMEText
import smtplib
from parametros import sigla_tribunal, nome_advogado, data_inicial, data_final
from destinatarios import recipient_list  # Import the list of recipient email addresses
import os
from dotenv import load_dotenv

load_dotenv('credentials.env')
print("Loaded .env file")

# Function to create the URL
def criar_url(sigla_tribunal, nome_advogado, data_inicial, data_final):
    url_base = "https://comunica.pje.jus.br/consulta"
    parametros = {
        'siglaTribunal': sigla_tribunal,
        'dataDisponibilizacaoInicio': data_inicial,
        'dataDisponibilizacaoFim': data_final,
        'nomeAdvogado': nome_advogado
    }
    return f"{url_base}?{urlencode(parametros)}"

# Function to open the page and collect content
async def abre_pagina_e_coleta_conteudo(url):
    navegador = await launch(headless=True)  # Run headless for efficiency
    pagina = await navegador.newPage()
    conteudo_total = {}  # Use a dictionary to count occurrences of content

    try:
        await pagina.goto(url, {'waitUntil': 'networkidle2'})
        print(f"Acessando URL: {url}")

        while True:
            try:
                # Wait for tribunal tabs to load
                await pagina.waitForSelector('.mat-tab-label-content', {'timeout': 10000})

                botoes_tribunais = await pagina.querySelectorAll('.mat-tab-label-content')
                for botao in botoes_tribunais:
                    try:
                        await botao.click()
                        await asyncio.sleep(1)  # Wait briefly to ensure content loads

                        await pagina.waitForSelector('.fadeIn', {'visible': True, 'timeout': 5000})

                        conteudo_tab_tribunais = await pagina.evaluate('''() => {
                            const processos = [];
                            const cards = document.querySelectorAll('.fadeIn');

                            cards.forEach(card => {
                                processos.push(card.innerText.trim());
                            });

                            return processos;
                        }''')

                        # Count occurrences of each content
                        for item in conteudo_tab_tribunais:
                            if item in conteudo_total:
                                conteudo_total[item] += 1
                            else:
                                conteudo_total[item] = 1

                    except Exception as erro:
                        print(f"Erro ao clicar na aba: {erro}")

            except Exception as erro:
                print(f"Erro em selecionar tribunais: {erro}")

            try:
                # Check if there's a next page button that is enabled
                botao_proxima_pagina = await pagina.querySelector('.ui-paginator-next:not(.ui-state-disabled)')
                
                if botao_proxima_pagina:
                    await botao_proxima_pagina.click()
                    await asyncio.sleep(4)  # Wait briefly to ensure page navigation
                    await pagina.waitForSelector('.fadeIn', {'visible': True, 'timeout': 10000})
                    print("Indo para a próxima página...")
                else:
                    print("Não há mais páginas para navegar.")
                    break
            except Exception as erro:
                print(f"Erro ao passar de página: {erro}")
                break

    except Exception as erro:
        print(f"Erro geral: {erro}")
    finally:
        await navegador.close()

    # Sort the content by the text (alphabetically) and unify duplicates
    if conteudo_total:
        conteudo_ordenado = sorted(conteudo_total.items(), key=lambda x: x[0])
        resultado_final = "\n\n".join([f"{item} (repetido {count} vezes)" if count > 1 else item for item, count in conteudo_ordenado])
        return resultado_final
    else:
        return "Não há conteúdo encontrado"

# Function to send email
def enviar_email(conteudo, destinatarios, sigla_tribunal, nome_advogado, data_inicial, data_final):
    remetente = os.getenv("EMAIL_ADDRESS")  # Fetch the sender email address from environment variables
    senha = os.getenv("EMAIL_PASSWORD")     # Fetch the email password from environment variables

    if not remetente or not senha:
        raise ValueError("Email credentials are not set in the environment variables.")

    try:
        # Set up the SMTP server (assuming OnMail uses SMTP)
        servidor = smtplib.SMTP('smtp.gmail.com', 587)  # Update with correct OnMail SMTP server and port

        servidor.starttls()  # Start TLS encryption
        servidor.login(remetente, senha)  # Log in to the OnMail account

        # Create the email
        email_body = (
            f"Tribunal: {sigla_tribunal}\n"
            f"Advogado: {nome_advogado}\n"
            f"Data Inicial: {data_inicial}\n"
            f"Data Final: {data_final}\n\n"
            "Conteúdo coletado:\n"
            f"{conteudo}"
        )

        # Create a MIMEText object for plain text email
        msg = MIMEText(email_body, 'plain')
        msg['From'] = remetente
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = "Resultados da Consulta"

        # Send the email
        servidor.sendmail(remetente, destinatarios, msg.as_string())
        servidor.quit()

        print("E-mail enviado com sucesso!")

    except smtplib.SMTPException as e:
        print(f"Erro ao enviar e-mail: {e}")

# Main function
async def funcao_principal():
    
    url_final = criar_url(sigla_tribunal, nome_advogado, data_inicial, data_final)
    conteudo = await abre_pagina_e_coleta_conteudo(url_final)
    
    print(url_final)
    print("Tribunal buscado:", sigla_tribunal)
    print("Nome do advogado buscado:", nome_advogado)
    print("Data inicial e final de buscas:", data_inicial, data_final)
    print("Conteúdo coletado:\n", conteudo)
    print(f"Tamanho do conteúdo coletado: {len(conteudo)} caracteres")
    
    # Email the results
    enviar_email(conteudo, recipient_list, sigla_tribunal, nome_advogado, data_inicial, data_final)

    print("E-mail enviado com sucesso!")

if __name__ == "__main__":
    asyncio.run(funcao_principal())
