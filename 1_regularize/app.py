import requests 
from bs4 import BeautifulSoup

#Body request
url         = 'https://www.listadevedores.pgfn.gov.br/api/devedores/'
nome        = "murilo varoto"
id          = "11462916988"
naturezas   = "00000000000"
payload     =  { "id": id, "naturezas": naturezas, "nome" : nome }
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.listadevedores.pgfn.gov.br",
    "Referer": "https://www.listadevedores.pgfn.gov.br/",
    "User-Agent": "Mozilla/5.0"
}
session = requests.Session()
resposta    = session.post(url, json=payload, headers=headers)

resposta.encoding = 'utf-8'
print( resposta.status_code )
print( resposta.json())
