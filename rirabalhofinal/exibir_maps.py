# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import csv
import os
app = Flask(__name__, template_folder=".")
GoogleMaps(app, key="")

@app.route("/")
def mapview():
    """""
    Ref: https://stackoverflow.com/questions/44218836/python-flask-googlemaps-get-users-current-location-latitude-and-longitude
    http://flaskgooglemaps.pythonanywhere.com/
    https://maps.googleapis.com/maps/api/geocode/json?address=brazil
    :return:
    """
    # locations = [(-9.6498487, -35.7089492), (-22.9068467, -43.1728965)]
    locations = []
    with open('dados/resultado2a.csv', 'r', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"', lineterminator='\n')
        try:
            for row in reader:
                if row['formatted_address'] and not row['formatted_address'].startswith('Brazil'):
                    if row['partido'] == 'Rede45':
                        icone = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                    elif row['partido'] == 'ptbrasil':
                        icone = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
                    else:
                        icone = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'

                    locations.append({'lat': row['lat'], 'lng': row['lng'], 'infobox': row['formatted_address'],
                                      'icon': icone})
        except Exception as e:
            print('ERRO %s' % str(e))
    mapa = Map(
        identifier="view-mapa",
        varname="mapa",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=5,
        markers=locations
    )
    return render_template('template.html', mapa=mapa)


@app.route("/palavras")
def palavras():
    locationsrede45 = []
    locationspt = []
    locationspmdb = []
    qtd_pos_rede45 = qtd_neg_rede45 = 0
    qtd_pos_pt = qtd_neg_pt = 0
    qtd_pos_pmdb = qtd_neg_pmdb = 0

    with open('dados/palavras_location_separadas2.csv', 'r', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"', lineterminator='\n')
        try:
            for row in reader:

                if row['tipo'] == 'pos':
                    icone = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                else:
                    icone = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'

                if row['partido'] == 'Rede45':
                    locationsrede45.append({'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'],
                                            'icon': icone})
                    if row['tipo'] == 'pos':
                        qtd_pos_rede45 += 1
                    else:
                        qtd_neg_rede45 += 1

                elif row['partido'] == 'ptbrasil':
                    locationspt.append(
                        {'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'], 'icon': icone})
                    if row['tipo'] == 'pos':
                        qtd_pos_pt += 1
                    else:
                        qtd_neg_pt += 1
                else:
                    locationspmdb.append(
                        {'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'], 'icon': icone})
                    if row['tipo'] == 'pos':
                        qtd_pos_pmdb += 1
                    else:
                        qtd_neg_pmdb += 1

        except Exception as e:
            print('ERRO %s' % str(e))

    maparede45 = Map(
        identifier="view-maparede45",
        varname="maparede45",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=4,
        markers=locationsrede45
    )

    maparedept = Map(
        identifier="view-mapapt",
        varname="maparede45",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=4,
        markers=locationspt
    )

    maparedepmdb = Map(
        identifier="view-mapapmdb",
        varname="maparede45",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=4,
        markers=locationspmdb
    )

    return render_template('palavras.html', maparede45=maparede45, maparedept=maparedept, maparedepmdb=maparedepmdb,
                           qtd_pos_rede45=qtd_pos_rede45, qtd_neg_rede45=qtd_neg_rede45,
                           qtd_pos_pt=qtd_pos_pt, qtd_neg_pt=qtd_neg_pt,
                           qtd_pos_pmdb=qtd_pos_pmdb, qtd_neg_pmdb=qtd_neg_pmdb)


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=True)

