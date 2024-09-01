import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pyppeteer import launch
from urllib.parse import urlencode
from parametros import nome_advogado, data_inicial, data_final, email_user, email_password, email_recipients

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
    conteudo_total = set()  # Use a set to avoid duplicates

    try:
        await pagina.goto(url, {'waitUntil': 'networkidle2'})

        while True:
            try:
                await pagina.waitForSelector('.fadeIn', {'timeout': 30000})

                botoes_tribunais = await pagina.querySelectorAll('.mat-tab-label-content')
                for botao in botoes_tribunais:
                    await botao.click()
                    await pagina.waitForSelector('.numero-unico-formatado', {'visible': True})

                    conteudo_tab_tribunais = await pagina.evaluate('''() => {
                        const processos = [];
                        const cards = document.querySelectorAll('.fadeIn');

                        cards.forEach(card => {
                            processos.push(card.innerText.trim());  // Collects all inner text from the card, including nested elements
                        });

                        return processos;
                    }''')

                    # Add to the set to avoid duplicates
                    conteudo_total.update(conteudo_tab_tribunais)

            except Exception as erro:
                print(f"Erro em selecionar tribunais: {erro}")

            try:
                botao_proxima_pagina = await pagina.querySelector('.ui-paginator-next:not(.ui-state-disabled)')
                if botao_proxima_pagina:
                    await botao_proxima_pagina.click()
                    await pagina.waitFor(2000)
                    await pagina.waitForSelector('.fadeIn', {'visible': True, 'timeout': 30000})
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

# Function to send email
def enviar_email(conteudo):
    remetente = email_user
    senha = email_password
    destinatarios = email_recipients  # This should be a list of email addresses

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = 'Resultados da Consulta'

    corpo_email = f"""
    Nome do advogado buscado: {nome_advogado}
    Data inicial e final de buscas: {data_inicial} até {data_final}
    
    Conteúdo:
    {conteudo}
    """
    
    msg.attach(MIMEText(corpo_email, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()
            servidor.login(remetente, senha)
            servidor.sendmail(remetente, destinatarios, msg.as_string())
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

async def funcao_principal():
    url_final = criar_url(nome_advogado, data_inicial, data_final)
    conteudo = await abre_pagina_e_coleta_conteudo(url_final)
    print("Nome do advogado buscado:", nome_advogado)
    print("Data inicial e final de buscas:", data_inicial, data_final)
    print("Conteúdo:", conteudo)
    enviar_email(conteudo)  # Send the collected content via email

if __name__ == "__main__":
    asyncio.run(funcao_principal())
