#!/usr/bin/python
# coding=utf-8
##############################################################################
#    Microsoft Translator API
#    @author Shawn Varghese
##############################################################################

#import websocket
import thread
import json
import requests
import urllib
#import wave
#import audioop
from time import sleep
import StringIO
import struct
import sys
import codecs
from xml.etree import ElementTree
import string
import re
from copy import deepcopy
import time
from collections import defaultdict
import os
LANGUAGES = ['en','es','pt','fr','ru']




def ConvertTextToLanguages(json_obj,trans_tweets):
    tokens = GetToken()
    #json_obj = [{'tweet_text':'All the APIs will have a free trial plan','lang':'en'},
    #            {'tweet_text':'Nouveautés sur les progrès en matière de lutte contre les abus en ligne','lang':'fr'},
    #            {'tweet_text':'If you have a special requirement','lang':'en'},
    #            {'tweet_text':'toca matar a su papa a su mamaá  sus hijitos, toda su familia','lang':'es'},
    #            {'tweet_text':'O hardware wireless rogue é fácil de introduzir','lang':'pt'},
    #            {'tweet_text':'Os pontos de acesso wireless são relativamente baratos e facilmente desdobrados','lang':'pt'}]
    
    counter = 0
    i=1
    total =0
    x = False
    for tweet in json_obj:
        #print tweetif tran
        if translated[tweet['id']]:
            tr_tweet = translated[tweet['id']]
            for lang in LANGUAGES:
                tweet['text_'+lang] = tr_tweet['text_'+lang]
            trans_tweets.append(tweet)
            print len(trans_tweets),"ALREADY TRANSLATED"
            total+=1
            continue
        if x:
            continue
        headers = {"Authorization ":tokens[i]}
        tweet_lang = tweet['tweet_lang']
        tweet_text = tweet.get('text_'+tweet_lang)
        if tweet_lang == 'es':
            continue
        escaped_text = re.escape(string.punctuation)
        #print tweet_text
        textToTranslate = re.sub(r'['+escaped_text+']', '',tweet_text).encode('utf-8')
        #print "original text ", textToTranslate
        translateLangs = deepcopy(LANGUAGES)
        if tweet_lang not in translateLangs:
            continue
        lang_count  = 0 
        for lang in translateLangs:
            key = 'text_%s' % lang
            translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&to={}".format(textToTranslate, lang)
            translation = textToTranslate

            if lang == tweet_lang:
                continue
            
            try:
                translationData = requests.get(translateUrl, headers = headers) #make request
                translation = ElementTree.fromstring(translationData.text.encode('utf-8')) # parse xml return values
                counter += 1
                #print "The translation is---> "+lang, translation.text #display translation
                if translation.text != None:
                    lang_count +=1
            except OSError:
                print "Could not translate %s" % textToTranslate
                translation = textToTranslate
                pass
            except KeyboardInterrupt:
                    x = True
                    continue
            tweet[key] = translation.text
        #print lang_count,len(LANGUAGES)
        if lang_count == len(LANGUAGES)-1:
            #json_obj.pop(tweet,'None')
            #translated[tweet['id']]=1
            #print len(trans_tweets)
            total+=1
            print total
            trans_tweets.append(tweet)
        if counter % 50 == 0:
            i = (i +1)%3
        
                #break

       
    return trans_tweets
            
def GetToken(): #Get the access token from ADM, token is good for 10 minutes
    client_ids = ['ir_project123','tbd_ir','IR-Engine']
    client_secret = ['uFbrAilfzXMjR1LqRZPSlTeCv20jSfP5N+Y1euQSeI4=','ZLVcwu78AnJNJsYzx9O4faNfKeyZpETfZs1eF4GZKGg=',
                    'tgDvNNtDLzzFUpwyTrR7ndWo9fGBodHvlLegOS2gctU=']
    
    urlArgs = list()
    for i in range(len(client_secret)):
        args = dict()
        args['client_id'] = client_ids[i]
        args['client_secret'] = client_secret[i]
        args['scope'] = 'http://api.microsofttranslator.com'
        args['grant_type'] = 'client_credentials'
        urlArgs.append(args)
    """
    urlArgs =[ {
        'client_id': 'ir_project123',
        'client_secret': 'uFbrAilfzXMjR1LqRZPSlTeCv20jSfP5N+Y1euQSeI4=',
        'scope': 'http://api.microsofttranslator.com',
        'grant_type': 'client_credentials'
    },{
            'client_id': 'tbd_ir',
        'client_secret': 'ZLVcwu78AnJNJsYzx9O4faNfKeyZpETfZs1eF4GZKGg=',
        'scope': 'http://api.microsofttranslator.com',
        'grant_type': 'client_credentials'
    }]
    """
    oauthUrl = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'

    try:
        tokens = list()
        for i in range(len(urlArgs)):
            oauthToken = json.loads(requests.post(oauthUrl, data = urllib.urlencode(urlArgs[i])).content) #make call to get ADM token and parse json
            finalToken = "Bearer " + oauthToken['access_token'] #prepare the token
            tokens.append(finalToken)
        #oauthToken2 = json.loads(requests.post(oauthUrl, data = urllib.urlencode(urlArgs[1])).content) #make call to get ADM token and parse json
        #finalToken2 = "Bearer " + oauthToken2['access_token'] #prepare the token
    except OSError:
        pass

    return tokens
 
#End GetTextAndTranslate()


if __name__ == "__main__":

    html_tweets = open('final/embed.json')
    translated = defaultdict(list)
    translated_path = 'final/translated.json'
    trans_tweets = list()
    if os.path.exists(translated_path):
        with open(translated_path) as tr:
            tr_data = json.load(tr)
            for tweet in tr_data:
                translated[tweet['id']]=tweet
                #trans_tweets.append(tweet)

    json_obj = json.load(html_tweets)
    #finalToken = GetToken()
    
    final_obj = ConvertTextToLanguages(json_obj,trans_tweets)
    print('testing')
    with open('final/translated.json','w') as results:
        json.dump(final_obj,results)

#end main