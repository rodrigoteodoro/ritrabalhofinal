# -*- coding: utf-8 -*-
import os
import requests
from json import loads, dumps
import csv
from time import sleep
import re
import difflib
try:
    import enchant
    tem_enchant = True
except:
    tem_enchant = False


def ajustar_csv_amostra():

    user_ids = []
    user_output = {}
    try:
        filename = 'dados/resultado.csv'
        if os.path.exists(filename):
            with open(filename, 'r') as csvfile, open('dados/amostrainicial.csv', 'w') as output:
                reader = csv.DictReader(csvfile, delimiter=';', quotechar='"', lineterminator='\n')
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';', quotechar='\"',
                                        lineterminator='\n',
                                        quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for row in reader:
                    user_partido = '%s-%s' % (row['userid'], row['partido'])
                    if user_partido not in user_ids and row['location'] and row['texto']:
                        user_ids.append(user_partido)
                        # TODO quem tem location: {'type': 'Point', 'coordinates': [-34.91021711, -8.11950282]}
                        # o valor é invertido na busca do google
                        if row['texto'] and (row['coordinates'] or (row['location'] and
                                                                        re.match('(\w{2,})+', row['location']) and
                                                                        not row['location'].startswith('Brasil'))):
                            if user_output.get(row['userid']) is None:
                                user_output[row['userid']] = {'username': row['username'], 'location': row['location']}

                            writer.writerow({'partido': row['partido'],
                                             'userid': row['userid'],
                                             'username': row['username'],
                                             'location': row['location'],
                                             'texto': row['texto'],
                                             'coordinates': row['coordinates']
                                             })

        if user_output:
            with open('dados/usuarios.csv', 'w') as usuarioscsv:
                writer = csv.DictWriter(usuarioscsv, fieldnames=['userid', 'username', 'location'],
                                        delimiter=';', quotechar='\"',
                                        lineterminator='\n',
                                        quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for k in user_output:
                    writer.writerow({'userid': k,
                                     'username': user_output.get(k).get('username'),
                                     'location': user_output.get(k).get('location')
                                     })

    except Exception as e:
        print('ERRO: %s' % str(e))


def ajustar_csv_api():
    """Ajuste o arquivo csv com os dados de localizacao corretos via api do google maps
    Ref: https://developers.google.com/maps/documentation/geocoding/start?hl=pt_BR"""

    # Guarda o id e partido do usuario para separar os comentarios repetidos e não repetir usuarios na amostra que for
    # retriada futuramente
    user_ids = []
    # Limite Free:
    # 2,500 free requests per day, calculated as the sum of client-side and server-side queries.
    # 50 requests per second, calculated as the sum of client-side and server-side queries.
    chave_api = None

    try:
        filename = 'dados/resultado.csv'
        if os.path.exists(filename):
            with open(filename, 'r') as csvfile, open('dados/resultado2.csv', 'w') as output:
                reader = csv.DictReader(csvfile, delimiter=';', quotechar='"', lineterminator='\n')
                fieldnames = reader.fieldnames
                fieldnames.append('formatted_address')
                fieldnames.append('lat')
                fieldnames.append('lng')
                fieldnames.append('lat_lng')
                writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';', quotechar='\"',
                                        lineterminator='\n',
                                        quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for row in reader:
                    user_partido = '%s-%s' % (row['userid'], row['partido'])
                    if user_partido not in user_ids and row['location'] and row['texto']:
                        user_ids.append(user_partido)

                        url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % row['location']
                        if chave_api:
                            url = '%s%s' % (url, str('&key=%s' % chave_api))
                        r = requests.get(url)
                        if r.status_code == 200:
                            j = loads(r.content.decode())
                            if j.get('results') and not j['results'][0]['formatted_address'].startswith(
                                    'Brazil') and 'Brazil' in j['results'][0]['formatted_address']:
                                writer.writerow({'partido': row['partido'],
                                                 'userid': row['userid'],
                                                 'username': row['username'],
                                                 'location': row['location'],
                                                 'texto': row['texto'],
                                                 'coordinates': row['coordinates'],
                                                 'formatted_address': j['results'][0]['formatted_address'],
                                                 'lat': j['results'][0]['geometry']['location']['lat'],
                                                 'lng': j['results'][0]['geometry']['location']['lng'],
                                                 'lat_lng': '%s,%s' % (j['results'][0]['geometry']['location']['lat'],
                                                                       j['results'][0]['geometry']['location']['lng']),
                                                 })
                        sleep(0.5)

    except Exception as e:
        print('ERRO: %s' % str(e))


def ajustar_csv_amostra_texto():

    palavras_erradas = []
    if tem_enchant:
        dicionario = enchant.Dict("pt_BR")
    try:
        filename = 'dados/resultado.csv'
        if os.path.exists(filename):
            with open(filename, 'r') as csvfile, open('dados/amostrainicialtexto.csv', 'w') as output:
                reader = csv.DictReader(csvfile, delimiter=';', quotechar='"', lineterminator='\n')
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';', quotechar='\"',
                                        lineterminator='\n',
                                        quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for row in reader:
                    if row['texto'] and re.match('([a-zA-Z]{3,})', row['texto']) and len(row['texto'].split(' ')) > 3:
                        texto_ajustado = ''
                        for s in row['texto'].split(' '):
                            p = re.match('((\w){2,})', s)
                            if p:
                                if row['partido'] == 'PMDB_Nacional' and p.group(0) == 'nacional':
                                    pass
                                else:
                                    if tem_enchant:
                                        if dicionario.check(p.group(0)):
                                            texto_ajustado += ' %s' % p.group(0)
                                        else:
                                            # sugestao = dicionario.suggest(p.group(0))
                                            # if sugestao:
                                            # print(p.group(0), sugestao)
                                            if s not in palavras_erradas:
                                                palavras_erradas.append(s)
                                    else:
                                        texto_ajustado += ' %s' % p.group(0)

                        if texto_ajustado:
                            writer.writerow({'partido': row['partido'],
                                             'userid': row['userid'],
                                             'username': row['username'],
                                             'location': row['location'],
                                             'texto': texto_ajustado,
                                             'coordinates': row['coordinates']
                                             })
        # if palavras_erradas:
            # print(palavras_erradas)

    except Exception as e:
        print('ERRO: %s' % str(e))


if __name__ == '__main__':
    # ajustar_csv_api()
    # ajustar_csv_amostra()
    ajustar_csv_amostra_texto()
