# -*- coding: utf-8 -*-

import sys, os
from time import sleep
import tweepy
from json import dumps
import re

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""


class Recuperar():
    """ Classe que recupera tweets e replies"""
    api = None

    partidos = ['Rede45', 'PMDB_Nacional', 'ptbrasil']

    calls_count = 0

    def __init__(self):
        pass

    def autenticar(self):

        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(auth, timeout=10, retry_count=3, retry_delay=10)
            return True
        except Exception as e:
            print('ERRO: %s' % str(e))

        return False

    def testar_limit_status(self):
        """Limites: There are two initial buckets available for GET requests:
        15 calls every 15 minutes, and 180 calls every 15 minutes."""
        aguardar = True
        aguardou = False
        msg_tela = True
        while aguardar:
            r = self.api.rate_limit_status()
            # print(r.get('resources'))
            if r.get('resources').get('application').get('/application/rate_limit_status').get('remaining') == 0 or r.get(
                    'resources').get('statuses').get('/statuses/retweets/:id').get('remaining') == 0 or r.get(
                    'resources').get('search').get('/search/tweets').get('remaining') == 0:
                if msg_tela:
                    print('Limite atingido, irá aguardar até no máximo 15 minutos! ')
                    msg_tela = False
                sleep(60)
                aguardou = True
            else:
                aguardar = False
        if aguardou:
            print('Continuando...')

    def recuperar_retweets(self, f):
        """ Recupera os retweets e armazena em f em formato csv
        :param f: FileHandler
        :return:
        """
        for partido in self.partidos:
            print('Tweets de %s' % partido)
            # u = self.api.get_user(partido)
            # print(type(u), u)
            self.testar_limit_status()
            result = self.api.user_timeline(partido, count=100)
            # result = self.api.user_timeline(partido, count=1, max_id=902665178990338049)
            # print('\nstatus\n')
            # print(type(result), result)
            for status in result:
                # print(type(status), status)
                # print(status.id, status.retweeted, status.text)
                self.testar_limit_status()
                retresult = self.api.retweets(status.id, count=100)
                # print('\nretweets\n')
                for retstatus in retresult:
                    # print(retstatus)
                    # print(retstatus.id, retstatus.retweeted, retstatus.text)
                    self.testar_limit_status()
                    u = self.api.get_user(retstatus.user.id)
                    # print(u.name, u.id, u.location)
                    if u.location:
                        f.write('"%s";%s;"%s";"%s"\n' % (partido, u.id, u.name, self.__ajustar_texto(u.location)))
                        f.flush()
                    sleep(0.5)

    def __ajustar_texto(self, texto, flag_lower=False):
        """ Remove caracteres especiais do texto e location
        :param texto:
        :return:
        """
        if texto:
            texto = texto.strip()
            texto = re.sub('((\n)|(\r))', '', texto)
            if flag_lower:
                texto = texto.lower()
            texto = ' '.join(
                re.sub("(@[A-Za-z0-9]+)|(#[A-Za-z0-9]+)|([^A-Za-z \tçéáíóãõúôêâ,;])|(\w+:\/\/\S+)",
                       " ", texto).split())
        return texto

    def recuperar_replies(self, f):
        """ Recupera os replies e armazena em f em formato csv
        :param f: FileHandler
        :return:
        """
        for partido in self.partidos:
            for m in [9]:
                for d in range(1, 8):
                    data = '2017-%02d-%02d' % (m, d)
                    print('Replies de %s na data %s ' % (partido, data))
                    self.testar_limit_status()
                    resultreply = self.api.search(to=partido, since=data, count=100)
                    for rreply in resultreply:
                        texto = self.__ajustar_texto(rreply.text.strip(), True)
                        if rreply.user.location and rreply.in_reply_to_status_id and texto:
                            f.write('"%s";%s;"%s";"%s";"%s";%s\n' % (partido,
                                                                     rreply.user.id,
                                                                     self.__ajustar_texto(rreply.user.name),
                                                                     self.__ajustar_texto(rreply.user.location),
                                                                     texto,
                                                                     str(rreply.coordinates if rreply.coordinates else '')))
                            f.flush()
                break

if __name__ == '__main__':
    try:
        r = Recuperar()
        ok = r.autenticar()
        # r.testar_limit_status()
        if ok:
            try:
                filename = 'dados/resultado.csv'
                existe = os.path.exists(filename)
                f = open(filename, 'a')
                if not existe:
                    f.write('partido;userid;username;location;texto;coordinates\n')
                    f.flush()
                r.recuperar_replies(f)
                # r.recuperar_retweets(f)
            finally:
                if f:
                    f.close()

    except Exception as e:
        print('ERRO: %s' % str(e))
    finally:
        sys.exit(0)
