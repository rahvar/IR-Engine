# -*- coding: utf-8 -*-
from app import app
from flask import render_template
from flask import request
from flask import jsonify
# from settings import APP_STATIC
import json
import pysolr
#import pysolr
#import urllib2
from urllib.request import urlopen

#solr = pysolr.Solr('http://localhost:8983/solr/VSM', timeout=10)

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
        filtered_lang_info[lang_info[i]] = item
    
    return render_template('index.html',tweets=results, lang_info=filtered_lang_info)

@app.route('/tags',methods=['POST'])
def tags():
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '0', "facet":"on", "facet.field":"hashtags"} 
    results = solr.search("*:*", **params)

    return jsonify(results.facets['facet_fields']['hashtags'])