# FAM Calendar update script

Script que almacena los dos próximos meses del calendario de la Federación de Atletismo de Madrid en Airtable y comunica los cambios en un bot de Telegram

## Consulta de próximas carreras

Vía bot de Telegram:
https://t.me/atletismofam

En formato listado: 
https://airtable.com/shrCwU0GaaKnM08g3

En formato calendario (exportable formato iCal):
https://airtable.com/embed/shrOf2x9anHwxUq9T/tblVB2deQdnPFrXWV?backgroundColor=red&viewControls=on&date=undefined&mode=undefined

## Acerca del script

Para instalar las dependencias correr:

```
pip install -r requirements.txt
```

Para replicarlo es necesario crear un bot y canal de Telegram y una tabla en airtable y actualizar en el fichero .env los valores correspondientes a API keys y IDs de chat / tabla.