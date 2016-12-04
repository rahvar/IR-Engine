# coding=utf-8
import os
import json
import re
from collections import defaultdict
from pprint import pprint
import time
import datetime

cwd = os.getcwd()
directory = cwd + "/data/"
filenames = list()


def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time laps in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt - dt.min).seconds
   # // is a floor division, not a comment on following line:
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

languages = ["en","es","tr","ko"]


#topics = ["politics",
#            "news",
#            "sports",
#            "tech",
#            "entertainment" ]
for subdir, dirs, files in os.walk(directory):
    
    for file in files:
        filenames.append(os.path.join(subdir, file))

output = list()
fileInfo = {}
unique = list()
topicCounter = defaultdict(int)
langCounter = defaultdict(int)
tweetExists = defaultdict(int)
dateCounter = defaultdict(int)
langTopicCount = defaultdict(int)
uniqueText = defaultdict(int)
test =0
retweeted_count =0
retweeted_lang_count = defaultdict(int)
check =True
count=0
for file in filenames:
    print file
    fileSplit = file.split("/")
    lang = fileSplit[-2]
    """
    if "Trump" in file or "Hillary" in file:
        topicInfo = topics[0]
    elif "Syria" in file:
        topicInfo = topics[1]
    elif "US Open" in file or "usopen" in file:
        topicInfo = topics[2]
    elif "Apple" in file or "iPhone" in file:
        topicInfo = topics[3]
    elif "GOT" in file or "Game of Thrones" in file:
        topicInfo = topics[4]
    else:
        topicInfo = "none"
    """
    with open(file) as tweetFile:
        data = json.load(tweetFile)

        for tweet in data:
          
            if tweetExists[tweet["id"]]:
                continue

            tweetExists[tweet["id"]] =1
            
            parsedTweet = dict()      
            parsedTweet["id"] = tweet["id"] 
            #parsedTweet["topic"] = topicInfo
            parsedTweet["tweet_lang"] = lang
            parsedTweet["tweet_text"] = tweet["text"]
            "<pre>(.*?)</pre>"
            test = datetime.datetime.strptime(tweet["created_at"],"%a %b %d %H:%M:%S +0000 %Y")
            res =  roundTime(test,roundTo = 60*60)
            finalDate = res.strftime('%Y-%m-%dT%H:%M:%SZ')
            date = finalDate[8:10]
            #if int(date) <7 or int(date)>14 or 'Aug' in tweet["created_at"] :
            #    continue 
         
            parsedTweet["tweet_date"] = finalDate

    
            if tweet["coordinates"]:
                parsedTweet["tweet_loc"] = ','.join(str(point) for point in tweet["coordinates"]["coordinates"][::-1])
                parsedTweet["lat"] = tweet["coordinates"]["coordinates"][1]
                parsedTweet["lng"] = tweet["coordinates"]["coordinates"][0]
            
            """ 
            emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons               
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

            
           
            finalEmList = list()
            if emoji_pattern.findall(tweet["text"]):
               
                emList = emoji_pattern.findall(tweet["text"])
                for em in emList:
                    if len(em)>1:
                        allEm = list(em)
                        finalEmList = finalEmList + allEm
                    else:
                        finalEmList.append(em)
            """
            #emoticons_pat = re.compile(":\)|;\-\)|:\-\)|:\(|:D|\(\^ω\^\)") 
            #emoticons = emoticons_pat.findall(tweet["text"])
            #if emoticons:
            #    finalEmList = finalEmList + emoticons
            if tweet['user']['location']:
                parsedTweet['location']  =  tweet['user']['location']

            lang_text = tweet["text"]

            #parsedTweet["tweet_urls"] = list()
            #url_pattern = re.compile("http\S+")
            #urlList = url_pattern.findall(tweet["text"])
            #if urlList: 
            #    parsedTweet["tweet_urls"] = urlList 
            parsedTweet['source'] = ''
            if tweet['source']:
                m = re.search('<a.*?>(.+?)</a>',tweet['source'])
                if m:
                    parsedTweet['source'] = m.group(1)
        
            parsedTweet["mentions"] = list()
            parsedTweet["hashtags"] = list()
            parsedTweet["media"] = list()

            original_text = tweet["text"] 
            for key in tweet["entities"].keys():
                for entity in tweet["entities"][key]:
                    if key == "user_mentions":
                        parsedTweet["mentions"].append(entity["screen_name"]) 
                    if key == "hashtags":
                        parsedTweet["hashtags"].append(entity["text"])
                    
                    if key == "media":
                        parsedTweet["media"].append(entity["media_url"])
                    
                    replaceText = original_text[entity["indices"][0]:entity["indices"][1]]
                    
                    lang_text = lang_text.replace(replaceText,"")
                    
            """
            for emoji in finalEmList:
                lang_text = lang_text.replace(emoji,"")
            """
            parsedTweet["text_"+lang] = re.sub(r'http\S+', '', lang_text)
        
            #parsedTweet["tweet_emoticons"] = finalEmList
        
            
            if 'retweeted_status' in tweet:
                retweeted_count+=1
                retweeted_lang_count[lang]+=1
            #if topicInfo == "none":
            #    print file

            if uniqueText[parsedTweet["text_"+lang]]:
                continue
            uniqueText[parsedTweet["text_"+lang]] =1

            langCounter[lang]+=1
            #dateCounter[parsedTweet["tweet_date"][0:10]]+=1
            #topicCounter[topicInfo]+=1
            #langTopicCount[lang + " "+topicInfo]+=1

            unique.append(tweet["id"])
            output.append(parsedTweet)

print "Total number of unique tweets is ",len(unique),len(set(unique)),len(unique)-len(set(unique))
print 
print dict(langCounter)
print 
print dict(dateCounter)
print 
print dict(topicCounter)
print 
print "Retweeted stats",retweeted_count,dict(retweeted_lang_count)
print 
for key in sorted(langTopicCount.keys()):
    print key,langTopicCount[key]
print len(uniqueText)
#print len(output)
#outFile = "final/output.json"
outFile = "final/parsedOutput.json"
with open(outFile,'w') as f:
    json.dump(output,f)

"""
with open(outFile) as readFile:
    data = json.load(readFile)
  
    ids =defaultdict(int)
    for tweet in data:
        ids[tweet["id"]]+=1

print max(ids.values())
"""

