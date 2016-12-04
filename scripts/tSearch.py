# coding=utf-8
import tweepy
import json
import datetime

consumer_key = "0EdS6AmwymOpueNFnV3yBnPQq"
consumer_secret = "wCs6Ke5gCWgF63pzbKlQTkaZ1sT6N0ue6GUkYjkiu6MgqlhtAw"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
access_token = "2807879286-8FL1iky7Jxe8XAl8YGtoDLmrO0IklHq4rbQzu3D"
access_token_secret = "0Kv7idR34Kc4Yf1H5DxWhzvfVlHLwyDhHsgw5dhuag2U5"
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,parser=tweepy.parsers.JSONParser(),wait_on_rate_limit=True,
                   wait_on_rate_limit_notify=True)


# User inputs
max_tweets = 12000
iterations = 50
retweeted_allow = 0
language = "ru"
#query = "#AppleEvent OR #iPhone7 OR AirPod OR #iPhonePlus OR #AirPod OR iPhone 7 OR Apple Keynote"
query = "Дональд Трамп"
topic = "Trump"
#topic = "US Open"
fileNumber = "f1"
#ts = time.time()
no_retweet_count = 0
#st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
date = datetime.date.today().strftime("%B %d - %Y")
directory = "data/" +language+"/"

# End user inputs
tweet_count =0

#since_date = "2016-12-1"
#until_date = "2016-12-3"
since_date = ""
until_date = ""
out = list()
try_count=0
sinceId = None
maxId = -1
while tweet_count < max_tweets and try_count<iterations:
    try_count+=1
    
    try:
        if maxId<0:
            if not sinceId:
                result = api.search(lang=language,q=query,count=1000,since = since_date, until=until_date)
            else:
                result = api.search(lang=language,q=query,count=1000,since_id=sinceId,since = since_date, until=until_date)
        else:
            if not sinceId:
                result= api.search(lang=language,q=query,count=1000,max_id = str(maxId-1),since = since_date, until=until_date)
            else:
                result= api.search(lang=language,q=query,count=1000,max_id = str(maxId-1),since_id =sinceId,since = since_date, until=until_date)
    except:
        print "Whoops"
    retweets=0
    print try_count
    if result['statuses']:
        new_tweets = result['statuses']
    else:
        continue
    if not new_tweets:
        print "No more tweets"
        break

    for res in new_tweets:
        #print try_count
        if 'retweeted_status' not in res or retweets<retweeted_allow:
            retweets+=1
            out.append(res)
    tweet_count += len(new_tweets)
    no_retweet_count = len(out)
    print try_count,tweet_count,no_retweet_count
    
    maxId = out[-1]['id']

fName = directory+"searchTweets_"+language+"_"+query+"_"+topic+"_"+date+"_"+str(no_retweet_count)+".json"


with open(fName,'w') as jsonData:
    json.dump(out,jsonData)