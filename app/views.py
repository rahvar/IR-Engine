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

@app.route('/query',methods=['GET'])
def query():
    search_string = request.args.get('usrquery', '*:*')
    if search_string == '':
        search_string = '*:*'
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    # params = {'rows': '100'} 
    results = solr.search(search_string)
    print(len(results))
    return render_template('index.html',tweets=results)


@app.route('/tags',methods=['POST'])
def tags():
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '0', "facet":"on", "facet.field":"hashtags"} 
    results = solr.search("*:*", **params)
    print(len(results))

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


    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '100'} 
    results = solr.search("*:*",**params)
  
    for r in results:
        print(r)
        break
    return render_template('index.html',tweets=results)




@app.route('/morelikethis')
def morelikethis():
    solr = pysolr.Solr('http://52.36.178.24:8983/solr/prj4/', timeout=10)
    tweet_id = request.args.get('similar')
    print('id:'+tweet_id)
    
    params = {'mlt':'true','mlt.mintf':'10','mlt.fl':'_text_','mlt.mindf':'1'}
    similar = solr.more_like_this('id:'+str(tweet_id), mltfl='_text_',**params)
    
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
