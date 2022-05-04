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

    currentMonth = datetime.now().month
    currentYear = 2022

    airtable = Table(config('AIRTABLE_APIKEY'), config('AIRTABLE_DOC_ID'),config('AIRTABLE_TABLE_ID'))

    records = records_new = list()

    for row in airtable.all():
        record = row['fields']
        if 'Reglamento' not in record:
            record['Reglamento'] = ''
        if 'Resultados' not in record:
            record['Resultados'] = ''
        if 'Inscritos' not in record:
            record['Inscritos'] = ''
        if 'Lugar' not in record:
            record['Lugar'] = ''

        records.append({
            'id': row['id'],
            'Nombre': record['Nombre'],
            'Fecha': record['Fecha'],
            'Lugar': record['Lugar'],
            'Reglamento':  record['Reglamento'],
            'Resultados':  record['Resultados'],
            'Inscritos': record['Inscritos'],
            'Categoría': record['Categoría']
        })
        
    # Gets all current and next month data
    if currentMonth == 12:
        months = [12,1]
        seasons = [currentYear, currentYear+1]
    else:
        months = [currentMonth, currentMonth+1, currentMonth+2]
        seasons = [currentYear, currentYear, currentYear]
        
    for index, month in enumerate(months):

        url = "https://www.atletismomadrid.com/index.php?option=com_content&view=article&id=3292&Itemid=111"
        data = {
            'temporada': seasons[index], 
            'mes': month, 
            'tipo': 'Todos'
        }

        page = requests.post(url, data).text

        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find('table', class_='calendario')

        for row in table.find_all('tr'):    

            cols = row.find_all('td')
            
            if(cols != []):

                date = datetime(seasons[index], month, int(cols[0].text.strip().split('.')[0].split('y')[0].split('-')[0]))

                name = cols[1].text.strip()
                place = cols[2].text.strip()
                rules = cols[3].a
                participants = cols[4].a
                results = cols[5].a

                if (rules is not None):
                    rules = re.sub("pdf?(.*)", "pdf", rules.get('href').strip().replace(" ", "%20"))
                else:
                    rules = ''

                if (participants is not None):
                    participants = re.sub("pdf?(.*)", "pdf", participants.get('href').strip().replace(" ", "%20"))
                else:
                    participants = ''


                if (results is not None):
                    results = re.sub("pdf?(.*)", "pdf", results.get('href').strip().replace(" ", "%20"))
                else:
                    results = ''
                
                category = cols[6].text.strip()

                x = next((x for x in records if x['Nombre'] == name), None)

                data = {
                    'Nombre': name, 
                    'Fecha': date.strftime("%Y-%m-%dT00:00:00.000Z"), 
                    'Lugar': place, 
                    'Reglamento': rules, 
                    'Categoría': category, 
                    'Resultados': results, 
                    'Inscritos': participants
                }
                
                if x is None:
                    airtable.create(data)
                    send_telegram('Nueva prueba disponible el ' + date.strftime('%d/%m/%Y') + ': ' + name)
                elif x['Reglamento'] != data['Reglamento']:
                    airtable.update(x['id'], data)
                    send_telegram('Nuevo reglamento disponible para la prueba ' + name + ' del ' + date.strftime('%d/%m/%Y') + ': ' + rules)
                elif x['Resultados'] != data['Resultados']:
                    airtable.update(x['id'], data)
                    send_telegram('Resultados disponibles para la prueba ' + name + ' del ' + date.strftime('%d/%m/%Y') + ': ' + results)
                elif x['Inscritos'] != data['Inscritos']:
                    airtable.update(x['id'], data)
                    send_telegram('Inscritos disponibles para la prueba ' + name + ' del ' + date.strftime('%d/%m/%Y') + ': ' + participants)

main()