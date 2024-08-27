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

async def abre_pagina_e_coleta_conteudo(url):
    browser = await launch()
    page = await browser.newPage()
    all_content = set()

    try:
        await page.goto(url, {'waitUntil': 'networkidle2'})

        while True:
            try:
                await page.waitForSelector('.numero-unico-formatado', {'timeout':30000})
                initial_content_texts = await page 