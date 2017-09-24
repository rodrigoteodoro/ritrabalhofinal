# -*- coding: utf-8 -*-
import os
import requests
from json import loads, dumps
import csv
import re
from PalavrasCategorizadas import stopwords

def separar_texto_location():
    location_list = []
    with open('dados/amostrainicialtexto.csv', 'r', encoding='utf-8') as input:
        reader = csv.DictReader(input, delimiter=';', quotechar='"', lineterminator='\n')
        for row in reader:
            if row['texto'] and ((row['location'] and re.match('(\w{2,})+', row['location']) and
                                      not row['location'].startswith('Brasil') and
                                      row['location'] != 'br')):
                # print(row['location'],  row['texto'])
                if row['location'] not in location_list:
                    location_list.append(row['location'])

    if location_list:
        with open('dados/localidades.csv', 'w',  encoding='utf-8') as output:
            writer = csv.DictWriter(output, fieldnames=['location', 'formatted_address', 'lat', 'lng', 'lat_lng'],
                                    delimiter=';', quotechar='\"',
                                    lineterminator='\n',
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for location in location_list:
                print('Recuperando: %s' % location)
                url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % location
                r = requests.get(url)
                if r.status_code == 200:
                    j = loads(r.content.decode())
                    if j.get('results') and not j['results'][0]['formatted_address'].startswith(
                            'Brazil') and 'Brazil' in j['results'][0]['formatted_address']:
                        writer.writerow({'location': location,
                                         'formatted_address': j['results'][0]['formatted_address'],
                                         'lat': j['results'][0]['geometry']['location']['lat'],
                                         'lng': j['results'][0]['geometry']['location']['lng'],
                                         'lat_lng': '%s,%s' % (j['results'][0]['geometry']['location']['lat'],
                                                               j['results'][0]['geometry']['location']['lng']),
                                         })
                else:
                    print('ERRO: %s' % r.status_code)


def separar_palavras_localidade():
    location_list = {}
    with open('dados/localidades.csv', 'r', encoding='utf-8') as input:
        reader = csv.DictReader(input, delimiter=';', quotechar='"', lineterminator='\n')
        for row in reader:
            location_list[row['location']] = {'formatted_address':row['formatted_address'],
                                              'lat':row['lat'],
                                              'lng':row['lng'],
                                              'lat_lng':row['lat_lng']
                                              }

    palavras_positivas = []
    palavras_negativas = []

    flag_corpus = 1

    if flag_corpus == 0:
        with open('dados/corpus-traduzido-positivo.csv', 'r', encoding='utf-8') as input:
            reader = csv.DictReader(input, delimiter=',', quotechar='"', lineterminator='\n',
                                    fieldnames=['eng', 'pt'])
            for row in reader:
                palavras_positivas.append(row['pt'])

        with open('dados/corpus-traduzido-negativo.csv', 'r', encoding='utf-8') as input:
            reader = csv.DictReader(input, delimiter=',', quotechar='"', lineterminator='\n',
                                    fieldnames=['eng', 'pt'])
            for row in reader:
                palavras_negativas.append(row['pt'])
        path_palavras_location = 'dados/palavras_location_separadas.csv'
    else:
        path_palavras_location = 'dados/palavras_location_separadas2.csv'
        reader_corpus = csv.DictReader(open('dados/corpus_positivo_negativo_from_LIWC2007_.csv', 'r'),
                                    fieldnames=['palavra', 'sentimento'],
                                    delimiter=';', quotechar='\"',
                                    lineterminator='\n',
                                    quoting=csv.QUOTE_NONNUMERIC)
        for row in reader_corpus:
            if row['sentimento'] == 'pos':
                palavras_positivas.append(row['palavra'])
            elif row['sentimento'] == 'neg':
                palavras_negativas.append(row['palavra'])

    palavra_location = {}
    tweets_per_user = {}
    with open('dados/amostrainicialtexto.csv', 'r', encoding='utf-8') as input:
        reader = csv.DictReader(input, delimiter=';', quotechar='"', lineterminator='\n')
        for row in reader:
            local = location_list.get(row['location'])
            if local:
                # Verifica se repete mesmo tweet para o mesmo usuario e partido, se repetir nao e importante
                user_partido = '%s_%s' % (row['partido'], row['userid'])
                if tweets_per_user.get(user_partido) is None:
                    tweets_per_user[user_partido] = []
                if row['texto'] in tweets_per_user[user_partido]:
                    continue
                else:
                    tweets_per_user[user_partido].append(row['texto'])
                    for palavra in row['texto'].split():
                        if palavra_location.get(row['partido']) is None:
                            palavra_location[row['partido']] = {}
                        if palavra not in stopwords and palavra_location[row['partido']].get(palavra) is None:
                            if palavra in palavras_positivas:
                                palavra_location[row['partido']][palavra] = {'location': []}
                                palavra_location[row['partido']][palavra]['tipo'] = 'pos'
                            elif palavra in palavras_negativas:
                                palavra_location[row['partido']][palavra] = {'location': []}
                                palavra_location[row['partido']][palavra]['tipo'] = 'neg'
                        if palavra_location[row['partido']].get(palavra) and palavra_location[row['partido']][palavra].get('tipo'):
                            palavra_location[row['partido']][palavra]['location'].append(local)

    with open(path_palavras_location, 'w',  encoding='utf-8') as output:
        writer = csv.DictWriter(output, fieldnames=['partido', 'palavra', 'tipo', 'lat', 'lng'],
                                delimiter=';', quotechar='\"',
                                lineterminator='\n',
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for partido in palavra_location:
            for palavra in palavra_location[partido]:
                for local in palavra_location[partido][palavra]['location']:
                    writer.writerow({'partido': partido,
                                     'palavra': palavra,
                                     'tipo': palavra_location[partido][palavra]['tipo'],
                                     'lat': local['lat'],
                                     'lng': local['lng']
                                     })


if __name__ == '__main__':
    # separar_texto_location()
    separar_palavras_localidade()

