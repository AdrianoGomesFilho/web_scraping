# WEB SCRAPING DJEN (Buscador de Intimações)

Este projeto é uma ferramenta baseada em Python para extrair informações de processos do Diário de Justiça Eletrônico Nacional (DJEN) e enviar os resultados por e-mail.

## Recursos

- Extrai informações de processos com base no tribunal, nome do advogado e intervalo de datas.
- Suporte a paginação e múltiplas abas do tribunal.
- Envia os resultados por e-mail usando SMTP.
- Configurável com `.env` para credenciais de e-mail.

## Tecnologias Utilizadas

- Python
- Pyppeteer (para automação de navegação web)
- smtplib (para envio de e-mails)
- dotenv (para gerenciamento de variáveis de ambiente)
- asyncio (para operações assíncronas)

## Instalação

1. Clone o repositório, instale os pacotes necessários e execute.
    
