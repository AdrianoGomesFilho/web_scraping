# WEB SCRAPING DJEN

This project is a Python-based tool to scrape case information from the PJE Tribunal website and send the results via email. It automates the process of querying tribunal information by fetching relevant data and sending it to a list of recipients.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [How It Works](#how-it-works)
- [License](#license)

## Features
- Scrapes case information based on tribunal, lawyer name, and date range.
- Supports pagination and multiple tribunal tabs.
- Filters and unifies duplicate case content.
- Sends the results via email using SMTP.
- Configurable with `.env` for email credentials.

## Installation

### Prerequisites
- Python 3.8+
- `pip` for Python package management.

### Dependencies
Install the required dependencies using `pip`:

```bash
pip install pyppeteer python-dotenv
```

### Cloning the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/AdrianoGomesFilho/web_scraping.git
```

## Usage

1. Update the necessary environment variables in `credentials.env` (see [Environment Variables](#environment-variables)).
2. Modify the parameters for tribunal code, lawyer name, and date range in `parametros.py`.
3. Create a list of email recipients in `destinatarios.py`.
4. Run the script:
```bash
python3 script.py
```

The script will scrape the DJEN (Diário de Justiça Eletrônico Nacional) data and email the results to the specified recipients.

## Environment Variables
You need to set the following environment variables in a file called `credentials.env`:

```
EMAIL_ADDRESS=<your_email_address>
EMAIL_PASSWORD=<your_email_password>
```

These will be used to log in and send emails via your SMTP server.

## How It Works

1. **URL Creation**: A URL is generated using the `criar_url` function based on the parameters provided (`sigla_tribunal`, `nome_advogado`, `data_inicial`, and `data_final`).
   
2. **Scraping Data**: The `abre_pagina_e_coleta_conteudo` function launches a headless browser with Pyppeteer, navigates through tribunal tabs, and collects case information from multiple pages.
   
3. **Content Unification and Sorting**: Duplicate case entries are counted, and the collected content is sorted alphabetically. Duplicate entries are combined and displayed with a count (e.g., "Content (repeated 3 times)").

4. **Sending Emails**: The `enviar_email` function compiles the content into a plain-text email, including search parameters at the top, and sends it to a predefined list of recipients using SMTP.

### Example Email Body:
```
Tribunal: TJSP
Advogado: João da Silva
Data Inicial: 2023-08-01
Data Final: 2023-08-31

Conteúdo coletado:
Processo 12345-67.2023.8.26.0001 (repetido 3 vezes)
Processo 98765-43.2023.8.26.0002
...
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
