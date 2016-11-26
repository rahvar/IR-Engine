#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#    Microsoft Translator API
#    @author Shawn Varghese
##############################################################################

import websocket
import thread
import json
import requests
import urllib
import wave
import audioop
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

LANGUAGES = ['en','es','pt','fr']

def ConvertTextToLanguages(json_obj,finalToken):
    json_obj = [{'tweet_text':'All the APIs will have a free trial plan','lang':'en'},
                {'tweet_text':'Nouveautés sur les progrès en matière de lutte contre les abus en ligne','lang':'fr'},
                {'tweet_text':'If you have a special requirement','lang':'en'},
                {'tweet_text':'toca matar a su papa a su mamaá  sus hijitos, toda su familia','lang':'es'},
                {'tweet_text':'O hardware wireless rogue é fácil de introduzir','lang':'pt'},
                {'tweet_text':'Os pontos de acesso wireless são relativamente baratos e facilmente desdobrados','lang':'pt'}]
    
    headers = {"Authorization ": finalToken}
    counter = 0
    for tweet in json_obj:
        tweet_text = tweet.get('tweet_text')
        escaped_text = re.escape(string.punctuation)
        textToTranslate = re.sub(r'['+escaped_text+']', '',tweet_text)
        tweet_lang = tweet.get('lang')
        print "original text ", textToTranslate
        translateLangs = deepcopy(LANGUAGES)
        if tweet_lang not in translateLangs:
            continue
        for lang in translateLangs:
            key = 'text_%s' % lang
            translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&to={}".format(textToTranslate, lang)
            translation = textToTranslate
            try:
                translationData = requests.get(translateUrl, headers = headers) #make request
                translation = ElementTree.fromstring(translationData.text.encode('utf-8')) # parse xml return values
                counter += 1
                print "The translation is---> ", translation.text #display translation
        
            except OSError:
                print "Could not translate %s" % textToTranslate
                translation = textToTranslate
                pass
            tweet[key] = translation.text
            if counter % 50 == 0:
                time.sleep(60)
    print json_obj
            
def GetToken(): #Get the access token from ADM, token is good for 10 minutes
    urlArgs = {
        'client_id': 'ir_project123',
        'client_secret': 'uFbrAilfzXMjR1LqRZPSlTeCv20jSfP5N+Y1euQSeI4=',
        'scope': 'http://api.microsofttranslator.com',
        'grant_type': 'client_credentials'
    }

    oauthUrl = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'

    try:
        oauthToken = json.loads(requests.post(oauthUrl, data = urllib.urlencode(urlArgs)).content) #make call to get ADM token and parse json
        finalToken = "Bearer " + oauthToken['access_token'] #prepare the token
    except OSError:
        pass

    return finalToken
 
#End GetTextAndTranslate()

if __name__ == "__main__":
    finalToken = GetToken()
    json_obj = {}
    ConvertTextToLanguages(json_obj,finalToken)
#end main