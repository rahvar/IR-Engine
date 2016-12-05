# -*- coding: utf-8 -*-
from app import app
from flask import render_template
from flask import request
from flask import jsonify
# from settings import APP_STATIC
import json
import pysolr
#import urllib2
from urllib.request import urlopen
from watson_developer_cloud import AlchemyLanguageV1
import ast
import re 
import string
import os
# from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
from collections import Counter

alchemy_language = AlchemyLanguageV1(api_key='b5abca00bba18cdda854cff13f3773df925a908b')
HOST = 'http://52.36.178.24:8983/solr/prj4/'
LANGUAGES = ['en','es','pt','fr']

@app.route('/query',methods=['GET'])
def query():
    selected_language = request.args.get('lang-select')
    search_string = request.args.get('usrquery', '*:*')
    if search_string == '':
        search_string = '*:*'
    solr = pysolr.Solr(HOST, timeout=10)
    
    params = {'rows': '1000','defType':'edismax','qf':'text_en^2 _txt_'} 
    results = solr.search(search_string,**params)
    
    tweet_text = ''
    count = 0
    
    escaped_text = re.escape(string.punctuation)
    
    for tweet in results:
        count += 1
        print(tweet)
        text = str(tweet['tweet_text'][0]).replace('[','').replace(']','')
#         text = re.sub(r'['+escaped_text+']', '',text)
#         text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
        tweet_text = '%s %s' % (tweet_text,text)
        
        if count > 3:
            break
    tweet_text = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet_text, flags=re.MULTILINE)
    tweet_text = re.sub(r'['+escaped_text+']', '',tweet_text)

    alchemy_response = {}
    if search_string != '*:*':
        alchemy_response = json.dumps(
        alchemy_language.combined(
          text=tweet_text,
          extract='entities,keywords',
          sentiment=1,
          max_items=1),
        indent=2)
    
    alchemy_response = ast.literal_eval(alchemy_response)
    
    tags = []
    dbpedia_link = ''
    for alchemy_result in alchemy_response.get('entities'):
        if alchemy_result.get('disambiguated'):
            if alchemy_result['disambiguated'].get('subType'):
                for tag in alchemy_result['disambiguated']['subType']:
                    tags.append(tag)
            if alchemy_result['disambiguated'].get('dbpedia'):
                dbpedia_link = alchemy_result['disambiguated'].get('dbpedia')
    
#     Get Summary text
    summary_data = ''
    if dbpedia_link != '':
        subject = dbpedia_link.replace('http://dbpedia.org/resource/','')
        summary_link = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s' % subject
        response = urlopen(summary_link)
        summary_data = json.loads(response.read().decode('utf8'))['query']['pages']
        summary_data = summary_data[list(summary_data.keys())[0]]['extract']
        summary_data = (summary_data[:200] + '..') if len(summary_data) > 75 else summary_data
        print(summary_data)

#     words_list = tweet_text.lower().replace('.','').replace('\n',' ').split(' ')
#     counter = Counter(words_list)
#     fopen = open('app/static/bubble/data/new_file.csv','w')
#     fopen.write("\"name\",\"word\",\"count\"")
#     fopen.write('\n')
#     for i in counter:
#         if counter[i] > 1 and i not in ['','i','the','to','a','to','him','of','el']:
#             str1 = '\"%s\",\"%s\",%s' % (i,i,counter[i])
#     #         fopen.write("\""+i+"\","+"\""+i+"\""+counter[i])
#             fopen.write(str1)
#             fopen.write('\n')
        
#     print("alchemy_response",alchemy_response)
#     alchemy_dict = ast.literal_eval(alchemy_response)
    
    return render_template('index.html',tweets=results,tags=tags,summary=summary_data)

@app.route('/tags',methods=['POST'])
def tags():
    solr = pysolr.Solr(HOST, timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '0', "facet":"on", "facet.field":"hashtags"} 
    results = solr.search("*:*", **params)
    
    return jsonify(results.facets['facet_fields']['hashtags'])

@app.route('/')
@app.route('/index')
def index():
    # response = urlopen('https://api.twitter.com/1.1/statuses/oembed.json?id=801219908910469120')
    # #data = json.loads('https://publish.twitter.com/oembed.json?url=https%3A%2F%2Ftwitter.com%2Fi%2Fmoments%2F650667182356082688')
    # data = json.loads(response.read().decode('utf8'))
    # response = urlopen('https://api.twitter.com/1.1/statuses/oembed.json?id=801086836764385280')
    # data2 = json.loads(response.read().decode('utf8'))
    # print data['html']

    solr = pysolr.Solr(HOST, timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '5'} 
    results = solr.search("*:*", **params)
    
    return render_template('index.html',tweets=results)

@app.route('/getLang',methods=['GET'])
def get_lang():
    data = json.dumps(
    alchemy_language.combined(
      text=request.args.get('query'),
      extract='entities,keywords',
      sentiment=1,
      max_items=1),
    indent=2)
    
    """
    data =  alchemy_language.combined(
        text='Donald Trump invites Hungarian PM #Orban to Washington:',
        extract='entities,keywords',
        sentiment=1,
        max_items=1)
    """
    data_dict = ast.literal_eval(data)
    return jsonify(data_dict)
