# -*- coding: utf-8 -*-
from app import app
from flask import render_template
import json
import os
import pysolr
#import urllib2
from urllib.request import urlopen

#solr = pysolr.Solr('http://localhost:8983/solr/VSM', timeout=10)

@app.route('/')
@app.route('/index')
def index():
    

    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    params = {
     'facet': 'on',
     'facet.field': ['tweet_lang','hashtags'],
     'facet.query':['{!tag =dt}tweet_lang:en'],
     'rows': '2',
    }
    results = solr.search("*:*",**params) 
    print(results.facets)
    #print(results)
    #print results['']
    #response = urlopen('https://api.twitter.com/1.1/statuses/oembed.json?id=801219908910469120')
    #data = json.loads('https://publish.twitter.com/oembed.json?url=https%3A%2F%2Ftwitter.com%2Fi%2Fmoments%2F650667182356082688')
    #data = json.loads(response.read().decode('utf8'))
    #response = urlopen('https://api.twitter.com/1.1/statuses/oembed.json?id=801086836764385280')
    #data2 = json.loads(response.read().decode('utf8'))
    #print data['html']
    #path = os.getcwd()
    #with open(path+'/embed.json') as data_file:    
    #data = json.load(data_file)
    #data = json.loads('embed.json')

    return render_template('index.html',info = results)