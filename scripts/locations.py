# coding=utf-8
import os
import urllib2
import urllib
import json
cwd = os.getcwd()


path  = cwd +'/final/parsedOutput.json'


url = 'http://maps.google.com/maps/api/geocode/json?address='
out = list()
if os.path.exists(path):
    with open(path) as tweets:
        emb_data = json.load(tweets)
        total = 0
        c = 0
        for tweet in emb_data:
            total+=1
            if 'lat' not in tweet and 'location' in tweet:
                place =  urllib.quote_plus(tweet['location'].encode('utf-8'))

                loc = url + place
                print loc
                response = urllib2.urlopen(loc)
                data = json.loads(response.read())
                if len(data['results']):
                    c+=1
                    tweet['lat'] = data['results'][0]['geometry']['location']['lat']
                    tweet['lng'] = data['results'][0]['geometry']['location']['lng']
            print c,total
            out.append(tweet)

outFile = "final/locationOutput.json"
with open(outFile,'w') as f:
    json.dump(out,f)
