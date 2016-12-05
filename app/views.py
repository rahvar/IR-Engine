# -*- coding: utf-8 -*-
from app import app
from flask import render_template
from flask import request
from flask import jsonify
# from settings import APP_STATIC
import json
import pysolr
from urllib.request import urlopen
from watson_developer_cloud import AlchemyLanguageV1
import ast
import re 
import string
import os
from collections import Counter

def lang_map(language):
    language_map = {'en':'English','fr':'French','ru':'Russian','es':'Spanish','pt':'Portuguese'}
    return language_map[language]

alchemy_language = AlchemyLanguageV1(api_key='b5abca00bba18cdda854cff13f3773df925a908b')
HOST = 'http://52.36.178.24:8983/solr/prj4/'
LANGUAGES = ['en','es','pt','fr']

@app.route('/')
@app.route('/query',methods=['GET'])
def query():
    selected_language = request.args.get('lang-select')
    search_string = request.args.get('usrquery', '')
    tweet_language = request.args.get('lang','')
    
    boost_language = 'tweet_lang:%s^3' % selected_language

    # base case params
    params = {'facet':'on', 'facet.field':'{!ex=dt}tweet_lang', 'rows':100,'defType':'edismax','bq':boost_language}

    # if not query, display everything
    if search_string == '' or search_string == 'undefined':
        search_string = '*:*'

    if tweet_language != '':
        languages = tweet_language.split(' ')
        # tweet_lang:en tweet_lang:es
        fq_content = ''
        for lang in languages:
            fq_content += "tweet_lang:"+lang+' '
        params['fq'] = '{!tag=dt}'+fq_content

    solr = pysolr.Solr(HOST, timeout=10)
    
    results = solr.search(search_string, **params)

    # extracting the tweet language
    lang_info = results.facets['facet_fields']['tweet_lang']
    filtered_lang_info = dict()

    for i in range(0,len(lang_info),2):
        item = []
        item.append(lang_info[i+1])
        if search_string is None:
            item.append("all")
        else:
            item.append(search_string)
        item.append(lang_map(lang_info[i]))
        filtered_lang_info[lang_info[i]] = item
    
    tweet_text = ''
    count = 0
    image_count = 0
    image_list = []
    
    escaped_text = re.escape(string.punctuation)
    for tweet in results:
        if count <= 3:
            text = str(tweet['tweet_text'][0]).replace('[','').replace(']','')
            tweet_text = '%s %s' % (tweet_text,text)
        count += 1
        
        if tweet.get('media'):
            print (tweet['media'])
            image_list.append(tweet['media'][0])
            image_count += 1

        if image_count > 3 and count > 3:
            break
    tweet_text = tweet_text = re.sub(r'http\S+', '', tweet_text)
    tweet_text = re.sub(r'['+escaped_text+']', '',tweet_text)

    alchemy_response = {}
    if search_string != '*:*':
        try:
            alchemy_response = json.dumps(
            alchemy_language.combined(
              text=tweet_text,
              extract='entities,keywords',
              sentiment=1,
              max_items=1),
            indent=2)
        except Exception:
            print ("Failed",Exception)
            pass

    tags = []
    dbpedia_link = ''
    
    if alchemy_response:
        alchemy_response = ast.literal_eval(alchemy_response)

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

    return render_template('index.html',lang_info=filtered_lang_info,tweets=results,tags=tags,summary=summary_data)

@app.route('/tags',methods=['POST'])
def tags():
    solr = pysolr.Solr(HOST, timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '0', "facet":"on", "facet.field":"hashtags"} 
    results = solr.search("*:*", **params)

    return jsonify(results.facets['facet_fields']['hashtags'])

@app.route('/morelikethis')
def morelikethis():
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    
    tweet_id = request.args.get('similar')

    params = {'mlt':'true','mlt.mintf':'7','mlt.fl':'_text_','mlt.mindf':'1','rows':100}   

    similar = solr.more_like_this('id:'+str(tweet_id), mltfl='_text_', **params)
    
    if len(similar)==0:
        similar = solr.search('id:'+tweet_id)
    
    return render_template('index.html',tweets=similar)

@app.route('/getLang',methods=['GET'])
def get_lang():
    data = json.dumps(
    alchemy_language.combined(
      text=request.args.get('query'),
      extract='entities,keywords',
      sentiment=1,
      max_items=1),
    indent=2)
    
    data_dict = ast.literal_eval(data)
    return jsonify(data_dict)

@app.route('/maps')
def maps():
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    params = {'rows': '1000000'} 
    results = solr.search("tweet_lat:*",**params)
    locations = list()
    #info = dict()
    for r in results:
        info = dict()
        info['lat'] = r['tweet_lat'][0]
        info['lng'] = r['tweet_long'][0]
        locations.append(info)
    
    return render_template('maps.html',results=json.dumps(locations))
