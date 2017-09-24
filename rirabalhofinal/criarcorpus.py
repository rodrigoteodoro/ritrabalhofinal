# -*- coding: utf-8 -*-

import csv
from PalavrasCategorizadas import palavras_negativas, palavras_positivas, stopwords


def gerar_stop_words(filepath, dicionario):
    with open(filepath, 'w') as outcsv:
        writer = csv.DictWriter(outcsv, fieldnames=['palavra'],
                                delimiter=';', quotechar='\"',
                                lineterminator='\n',
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for k in dicionario:
            writer.writerow({'palavra': k})


if __name__ == '__main__':
    # gerar_stop_words('dados/stopwords.csv', stopwords)
    #gerar_stop_words('dados/palavras_positivas.csv', palavras_positivas)
    #gerar_stop_words('dados/palavras_negativas.csv', palavras_negativas)
    pass