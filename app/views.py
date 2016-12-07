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
import datetime
from collections import Counter

alchemy_language = AlchemyLanguageV1(api_key='b5abca00bba18cdda854cff13f3773df925a908b')
# HOST = 'http://35.165.140.166:8983/solr/prj4/'
HOST = 'http://localhost:8983/solr/prj4/'
# LANGUAGES = ['en','es','pt','fr','ru']

def lang_map(language):
    language_map = {'en':'English','fr':'French','ru':'Russian','es':'Spanish','pt':'Portuguese'}
    return language_map[language]

@app.route('/')
@app.route('/query',methods=['GET'])
def query():

    # Retrieve the parameter values from the url
    selected_language = request.args.get('lang-select')
    search_string = request.args.get('usrquery', '')
    tweet_language = request.args.get('lang','')

    # DATE ARGS
    from_date = request.args.get('datefrom','')
    to_date = request.args.get('dateto','')
    
    # Query Boosting
    boost_language = 'tweet_lang:%s^3' % selected_language

    # base case params
    params = {'facet':'on', 'facet.field':['{!ex=dt}tweet_lang','tweet_date'], 'rows':100,'defType':'edismax','bq':boost_language}

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

        if from_date and to_date:
            date_range = 'tweet_date:['+from_date+' TO ' + to_date+ ']'
            params['fq'] += ' ' + date_range
    else:
        if from_date and to_date:
            date_range = 'tweet_date:['+from_date+' TO ' + to_date+ ']'
            params['fq'] = date_range

    solr = pysolr.Solr(HOST, timeout=10)
    
    results = solr.search(search_string, **params)

    # extracting the tweet language
    lang_info = results.facets['facet_fields']['tweet_lang']

    # extracting the tweet date
    date_results = results.facets['facet_fields']['tweet_date']

    """
     ---------- LANGUAGE FACETING STARTS HERE ------
    """
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
    """
     ---------- LANGUAGE FACETING ENDS HERE ------
    """

    """
     ---------- DATE FACETING STARTS HERE ------
    """
    dates = list()
    date_info = list()
    #print(date_results)
    for i in range(0,len(date_results),2):
    
        d = date_results[i][0:10]
        date_object = datetime.datetime.strptime(d,'%Y-%m-%d')
        dates.append(date_object)

    lower_date = min(dates)
    upper_date = max(dates)

    date_info.append({'y':lower_date.year,'m':lower_date.month,'d':lower_date.day})
    date_info.append({'y':upper_date.year,'m':upper_date.month,'d':upper_date.day})

    """
     ---------- DATE FACETING ENDS HERE ------
    """
    
    tweet_text = search_string
    count = 0

    image_list = []
    image_count = 0

    
    for tweet in results:
        if count <= 3:
            text = str(tweet['tweet_text'][0]).replace('[','').replace(']','')
            tweet_text = '%s %s' % (tweet_text,text)
        count += 1
        
        if tweet.get('media') and search_string != '*:*':
            image_list.append(tweet['media'][0])
            image_count += 1
 
        if (image_count > 4 and count > 3) or (count > 100):
            break
#         if count > 3:
#             break;
    
    if search_string == '*:*':
        image_list = []
    
    escaped_text = re.escape(string.punctuation)
    tweet_string = ''
    for tweet in results:
        text = str(tweet['tweet_text'][0]).replace('[','').replace(']','')
        tweet_string = '%s %s' % (tweet_string,text)
        tweet_string = re.sub(r'http\S+', '', tweet_string)
        tweet_string = re.sub(r'['+escaped_text+']', '',tweet_string)

    tweet_text = re.sub(r'http\S+', '', tweet_text)
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
    
    # Get Summary text
    summary_data = ''
    if dbpedia_link != '':
        subject = dbpedia_link.replace('http://dbpedia.org/resource/','')
        if selected_language and selected_language != 'en':
            summary_link = 'https://%s.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s' % (selected_language,subject)
            response = urlopen(summary_link)
            summary_data = json.loads(response.read().decode('utf8'))['query']['pages']
            summary_data = summary_data[list(summary_data.keys())[0]].get('extract')
        elif selected_language == 'en' or not summary_data or not selected_language:
            summary_link = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s' % subject
            response = urlopen(summary_link)
            summary_data = json.loads(response.read().decode('utf8'))['query']['pages']
            summary_data = summary_data[list(summary_data.keys())[0]].get('extract')
        if summary_data:
            summary_data = (summary_data[:200] + '..') if len(summary_data) > 75 else summary_data



    # Return the results and render it on the html page
    return render_template('index.html',date_info=json.dumps(date_info),lang_info=filtered_lang_info,tweets=results,tags=tags,summary=summary_data,image_list=image_list)

# To handle tags on html
@app.route('/tags',methods=['POST'])
def tags():
    solr = pysolr.Solr(HOST, timeout=10)
    # results = solr.search("*:*")
    params = {'rows': '0', "facet":"on", "facet.field":"hashtags"} 
    results = solr.search("*:*", **params)

    return jsonify(results.facets['facet_fields']['hashtags'])

# Retrieve Similar pages 
@app.route('/morelikethis')
def morelikethis():
    solr = pysolr.Solr(HOST, timeout=10)
    
    tweet_id = request.args.get('similar')

    params = {'mlt':'true','mlt.mintf':'7','mlt.fl':'_text_','mlt.mindf':'1','rows':100}   

    similar = solr.more_like_this('id:'+str(tweet_id), mltfl='_text_', **params)
    
    if len(similar)==0:
        similar = solr.search('id:'+tweet_id)
    
    return render_template('index.html',tweets=similar)

# Language detector
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


# Maps 
@app.route('/maps')
def maps():
    solr = pysolr.Solr(HOST, timeout=10)
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
