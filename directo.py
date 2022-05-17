# coding=utf8
import requests
import re
from decouple import config
from datetime import datetime
from bs4 import BeautifulSoup
from pyairtable import Table, formulas

def send_telegram(message):

    url = "https://api.telegram.org/bot" + config('TELEGRAM_BOT_TOKEN') + "/sendMessage?chat_id=" + config('TELEGRAM_CHAT_ID') + "&text=" + message
    response = requests.get(url)
    return response

def main():

    airtable = Table(config('AIRTABLE_APIKEY'), config('AIRTABLE_DOC_ID'),config('AIRTABLE_DIRECTOS_TABLE_ID'))

    records = records_new = list()

    for row in airtable.all():
        record = row['fields']
        
        if 'URL' not in record:
            record['URL'] = ''

        records.append({
            'id': row['id'],
            'Nombre': record['Nombre'],
            'URL': record['URL']
        })

    url = "https://www.atletismomadrid.com/"
    page = requests.get(url).text

    soup = BeautifulSoup(page, 'html.parser')

    for div in soup.find_all('div', class_='sp-module-content'):    

        title = div.find('h2')
        
        if title is not None and (title.text == "Result. en Directo"):

            competitions = div.find('div', class_='compt_circu_principal').find_all('li')

            for competition in competitions:

                name = competition.a.text
                url = "https://www.atletismomadrid.com/" + competition.a.get('href').strip().replace(" ", "%20")

                x = next((x for x in records if x['Nombre'] == name and x['URL']== url), None)

                data = {
                    'Nombre': name, 
                    'URL': url
                }
                
                if x is None:
                    airtable.create(data)
                    send_telegram('Resultados en directo disponibles para ' + name + ': ' + url)
                    
main()