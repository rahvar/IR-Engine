# coding=utf-8
import os
import json
import re
from collections import defaultdict
from pprint import pprint
import time
import datetime
import urllib2 
from collections import defaultdict
cwd = os.getcwd()
directory = cwd + "/data/"
filenames = list()

path  = cwd +'/final/locationOutput.json'
embed_path = cwd + '/final/embed.json'
emb_dict = defaultdict(int)

out = list()
url = "https://api.twitter.com/1.1/statuses/oembed.json?id="

if os.path.exists(embed_path):
    with open(embed_path) as tweets:
        emb_data = json.load(tweets)

        for tweet in emb_data:
            if 'html' in tweet.keys():
                emb_dict[tweet['id']] =tweet['html']
            else:
                print "WTF"
with open(path) as tweets:
    data = json.load(tweets)
    count =0
    for tweet in data:
        count+=1
        if not emb_dict[tweet['id']]:

            
            fin = url + str(tweet['id'])
            print count
            try:
                response = urllib2.urlopen(fin)
                embed = json.loads(response.read())
                tweet['html'] = embed['html']
            except Exception:
                print "WHY?"
                continue
            except KeyboardInterrupt:
                break 
        else:
            #print "ALREADY DONE"
            tweet['html'] = emb_dict[tweet['id']]
        out.append(tweet)


outFile = "final/embed.json"
with open(outFile,'w') as f:
    json.dump(out,f)