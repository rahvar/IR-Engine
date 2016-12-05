# -*- coding: utf-8 -*-
from app import app
from flask import render_template
from flask import request
from flask import jsonify
# from settings import APP_STATIC
import json
import pysolr
from urllib.request import urlopen

def lang_map(language):
    language_map = {'en':'English','fr':'French','ru':'Russian','es':'Spanish','pt':'Portuguese'}
    return language_map[language]

@app.route('/')
@app.route('/query',methods=['GET'])
def query():
    search_string = request.args.get('usrquery', '')
    tweet_language = request.args.get('lang','')
    print("Tweet language: ",tweet_language)

    # base case params
    params = {'facet':'on', 'facet.field':'{!ex=dt}tweet_lang', 'rows':100}

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

    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    
    print(params)
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
    
    return render_template('index.html',tweets=results, lang_info=filtered_lang_info)

@app.route('/tags',methods=['POST'])
def tags():
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '0', "facet":"on", "facet.field":"hashtags"} 
    results = solr.search("*:*", **params)

    return jsonify(results.facets['facet_fields']['hashtags'])

@app.route('/morelikethis')
def morelikethis():
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    
    tweet_id = request.args.get('similar')

    print('id:'+tweet_id)
    
    params = {'mlt':'true','mlt.mintf':'7','mlt.fl':'_text_','mlt.mindf':'1','rows':100}   

    similar = solr.more_like_this('id:'+str(tweet_id), mltfl='_text_', **params)
    
    if len(similar)==0:
          similar = solr.search('id:'+tweet_id)
    
    return render_template('index.html',tweets=similar)

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
