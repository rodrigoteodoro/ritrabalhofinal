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
    locationsrede45 = []
    locationspt = []
    locationspmdb = []

    with open('resultado2a.csv', 'r', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"', lineterminator='\n')
        try:
            for row in reader:
                if row['formatted_address'] and not row['formatted_address'].startswith('Brazil'):

                    if row['partido'] == 'Rede45':
                        locationsrede45.append({'lat': row['lat'], 'lng': row['lng'], 'infobox': row['formatted_address'], 'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'})
                    elif row['partido'] == 'ptbrasil':
                        locationspt.append({'lat': row['lat'], 'lng': row['lng'], 'infobox': row['formatted_address'], 'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'})
                    else:
                        locationspmdb.append({'lat': row['lat'], 'lng': row['lng'], 'infobox': row['formatted_address'], 'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'})

        except Exception as e:
            print('ERRO %s' % str(e))

    maparede45 = Map(
        identifier="view-maparede45",
        varname="mapa",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=5,
        markers=locationsrede45
    )

    mapapt = Map(
        identifier="view-mapapt",
        varname="mapa",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=5,
        markers=locationspt
    )

    mapapmdb = Map(
        identifier="view-mapapmdb",
        varname="mapa",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=5,
        markers=locationspmdb
    )

    return render_template('template.html', maparede45=maparede45, mapapt=mapapt, mapapmdb=mapapmdb)


@app.route("/palavras")
def palavras():
    locationsrede45 = []
    locationsrede45neg = []
    locationspt = []
    locationsptneg = []
    locationspmdb = []
    locationspmdbneg = []
    qtd_pos_rede45 = qtd_neg_rede45 = 0
    qtd_pos_pt = qtd_neg_pt = 0
    qtd_pos_pmdb = qtd_neg_pmdb = 0

    with open('palavras_location_separadas2.csv', 'r', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"', lineterminator='\n')
        try:
            for row in reader:

                if row['tipo'] == 'pos':
                    icone = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                else:
                    icone = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'

                if row['partido'] == 'Rede45':

                    if row['tipo'] == 'pos':
                        locationsrede45.append({'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'],
                                                'icon': icone})
                        qtd_pos_rede45 += 1
                    else:
                        locationsrede45neg.append({'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'],
                                                   'icon': icone})
                        qtd_neg_rede45 += 1

                elif row['partido'] == 'ptbrasil':

                    if row['tipo'] == 'pos':
                        locationspt.append(
                            {'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'], 'icon': icone})
                        qtd_pos_pt += 1
                    else:
                        locationsptneg.append(
                            {'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'], 'icon': icone})
                        qtd_neg_pt += 1
                else:
                    if row['tipo'] == 'pos':
                        locationspmdb.append(
                            {'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'], 'icon': icone})
                        qtd_pos_pmdb += 1
                    else:
                        locationspmdbneg.append(
                            {'lat': row['lat'], 'lng': row['lng'], 'infobox': row['palavra'], 'icon': icone})
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
        markers=locationsrede45,
        cluster=False
    )

    maparede45neg = Map(
        identifier="view-maparede45neg",
        varname="maparede45",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=4,
        markers=locationsrede45neg,
        cluster=False
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
    maparedeptneg = Map(
        identifier="view-mapaptneg",
        varname="maparede45",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=4,
        markers=locationsptneg
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

    maparedepmdbneg = Map(
        identifier="view-mapapmdbng",
        varname="maparede45",
        style="height:600px;width:1024px;margin:0;",
        lat=-14.235004,
        lng=-51.92528,
        zoom=4,
        markers=locationspmdbneg
    )

    return render_template('palavras.html',
                           maparede45=maparede45, maparede45neg=maparede45neg,
                           maparedept=maparedept, maparedeptneg=maparedeptneg,
                           maparedepmdb=maparedepmdb, maparedepmdbneg=maparedepmdbneg,
                           qtd_pos_rede45=qtd_pos_rede45, qtd_neg_rede45=qtd_neg_rede45,
                           qtd_pos_pt=qtd_pos_pt, qtd_neg_pt=qtd_neg_pt,
                           qtd_pos_pmdb=qtd_pos_pmdb, qtd_neg_pmdb=qtd_neg_pmdb)


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=True)

