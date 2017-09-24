# -*- coding: utf-8 -*-

from lxml import html
import requests
import tempfile
import matplotlib.pyplot as plt
import csv
import collections

from PalavrasCategorizadas import stopwords

categoria = {}
dicionario = {}


def ler_dicionario(arquivo):
    """http://www.nilc.icmc.usp.br/portlex/index.php/pt/projetos/liwc
     Le o arquivo de dicionario e o separa em categoria e faz a tradução dos numeros para as categorias
    :param arquivo: (filehandler) Handler do arquivo
    :return:
    """
    idx = 0
    for linha in arquivo.readlines():
        if linha:
            idx +=1
            linha = linha.decode('iso-8859-1')
            if idx < 66:
                linha = linha.replace('\r\n', '').split('\t')
                if len(linha) == 2:
                    categoria[linha[0]] = linha[1]
            if idx > 66:
                linha = linha.replace('\r\n', '').split('\t')
                tipo = []
                for t in linha[1:]:
                    tipo.append(categoria.get(t))
                dicionario[linha[0]] = tipo


def extrair_posemo_negemo():
    palavras_sent = {}

    for p in dicionario:
        if '*' not in p:
            if 'posemo' in dicionario[p]:
                palavras_sent[p] = 'pos'
            if 'negemo' in dicionario[p]:
                palavras_sent[p] = 'neg'

    if palavras_sent:
        od = collections.OrderedDict(sorted(palavras_sent.items()))
        writer_pos = csv.DictWriter(open('dados/corpus_positivo_negativo_from_LIWC2007_.csv', 'w'),
                                    fieldnames=['palavra', 'sentimento'],
                                    delimiter=';', quotechar='\"',
                                    lineterminator='\n',
                                    quoting=csv.QUOTE_NONNUMERIC)
        writer_pos.writeheader()
        for k, v in od.items():
            writer_pos.writerow({'palavra': k, 'sentimento': v})

    return None


def verificar_palavra(palavra):
    """Dado uma palavra verifica a categoria que ela se encontra
    :param palavra:
    :return: array com as categorias ou array vazio se não encontrada
    """
    r = dicionario.get(palavra)
    return r if r else []


idx_grafico = 0


def analizar_texto(texto, nome):
    categorias_qtd = {}
    positivas_negativas = [0,0]
    for palavra in texto.split(' '):
        if palavra not in stopwords:
            categorias = verificar_palavra(palavra)
            if categorias:
                # print(palavra, categorias)
                # palavrão somente em uma categoria
                for c in categorias:
                    if c in ['anger', 'sad', 'feel', 'body', 'health', 'sexual', 'time', 'work','achieve', 'leisure', 'home', 'money', 'relig', 'death', 'swear']:
                        if categorias_qtd.get(c) is None:
                            categorias_qtd[c] = 1
                        else:
                            categorias_qtd[c] += 1
                    elif c == 'posemo':
                        positivas_negativas[0] += 1
                    elif c == 'negemo':
                        positivas_negativas[1] += 1

    if categorias_qtd:
        # https://pythonspot.com/en/matplotlib-pie-chart/
        # Data to plot
        labels = []
        sizes = []
        for c in categorias_qtd:
            labels.append(c)
            sizes.append(categorias_qtd.get(c))

        global idx_grafico
        # Categorias
        idx_grafico += 1
        plt.figure(idx_grafico)
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False, startangle=140)
        plt.axis('equal')
        plt.title(nome)

        # positivos/negativos
        idx_grafico += 1
        plt.figure(idx_grafico)
        plt.pie(positivas_negativas, labels=['Positivo', 'Negativo'], autopct='%1.1f%%', shadow=False, startangle=90,
                colors=['#4da6ff', '#ff4d4d'])
        plt.axis('equal')
        plt.title(nome)
        #plt.show()

    else:
        print('Nenhuma categoria encontrada!')


def analisar_musica(url):
    r = requests.get(url)
    if r.status_code == 200:
        # http://docs.python-guide.org/en/latest/scenarios/scrape/
        tree = html.fromstring(r.content)
        letra = tree.xpath('//div[@itemprop="description"]/text()')
        nome = tree.xpath('//h1/text()')
        if letra:
            letra = (' '.join(letra)).replace('\n', '')
            nome = (' '.join(nome)).replace('\n', '')
            analizar_texto(letra, nome)


def lista_musicas():
    """ Lista de musicas para gerar os graficos
    :return:
    """
    analisar_musica('https://www.vagalume.com.br/claudinho-buchecha/fico-assim-sem-voce-2.html')
    # analisar_musica('https://www.vagalume.com.br/legiao-urbana/o-teatro-dos-vampiros.html')
    plt.show()
    pass


if __name__ == '__main__':
    # Recupera o arquivo da internet
    r = requests.get('http://143.107.183.175:21380/portlex/images/arquivos/liwc/LIWC2007_Portugues_win.dic.txt')
    if r.status_code == 200:
        fp = tempfile.TemporaryFile()
        fp.write(r.content)
        fp.seek(0)
        ler_dicionario(fp)
        # Exemplos de uso
        # for p in ['bonito', 'feio', 'carro', 'beijo']:
        #    print(p, ':', ','.join(verificar_palavra(p)))
        # lista_musicas()
        extrair_posemo_negemo()
