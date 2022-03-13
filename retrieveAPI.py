import requests as requests
from requests_oauthlib import OAuth2Session
import json
import re
import time
import datetime

# it works but it seems to disconnect at some point

API_HOST = "https://sandbox-oauth.piste.gouv.fr/"
TOKEN_URL = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
client_id = "client_id"
client_secret = "client_secret"

article = []

for year in range(1980, 2023):
    tokencall = requests.post(TOKEN_URL, data={
                              "grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret, "scope": "openid"})
    token = tokencall.json()
    client = OAuth2Session(client_id, token=token)
    date = str(year) + '-01-02'
    resp = client.post(
        "https://sandbox-api.piste.gouv.fr/dila/legifrance-beta/lf-engine-app/consult/code/tableMatieres",
        headers={'accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer hwpwT5k580MDDXZym8PPMhLV6MhvJnSBf7OpQmer85XQzWYjiVl8Jt'}, data=json.dumps({
                     "date": date,
                     "textId": "LEGITEXT000006069577"
                 }))
    book = json.loads(resp.content.decode('utf-8'))
    my_new_date = int(time.mktime(
        datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()))*1000
    LEGIARTI_list = re.findall(
        r'"cid": "LEGIARTI.............', json.dumps(book))

    for id_article in LEGIARTI_list:
        my_list = id_article.replace("\"", "").replace(" ", "").split(':')
        my_obj = {my_list[0]: my_list[1]}
        resp_article = client.post(
            "https://sandbox-api.piste.gouv.fr/dila/legifrance-beta/lf-engine-app/consult/getArticleByCid",
            headers={'accept': 'application/json',
                     'Content-Type': 'application/json',
                     'Authorization': 'Bearer hwpwT5k580MDDXZym8PPMhLV6MhvJnSBf7OpQmer85XQzWYjiVl8Jt'}, data=json.dumps(my_obj))
        if resp_article == {}:
            continue
        content = json.loads(resp_article.content.decode('utf-8'))

        for version in content['listArticle']:
            if version['dateDebut'] < my_new_date and version['dateFin'] > my_new_date:
                article.append({
                    'year': year,
                    'from': version['dateDebut'],
                    'to': version['dateFin'],
                    'id': version['id'],
                    'name': 'Article ' + version['num'],
                    'content': version['texte']
                })
