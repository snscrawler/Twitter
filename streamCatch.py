
import oauth2
import urllib
import json
import urllib.request
import datetime
import time

#from config import *
CONSUMER_KEY = "MlQHYIaVcsmjr2h4defzRi88H"
CONSUMER_SECRET = "2u7cPGQwiNLMQHpZh0iw0qEj6aJB6INQw35FSlnwfyL0tIlmdU"
ACCESS_TOKEN = "836816176235888640-6lFKqe8OkkUA8NxYz6cWRdv7cJTEALb"
ACCESS_SECRET = "XjrusK6qGpZtrIZkNgq4fjV8oZLO5DF7FZtrs1RxQnF4X"

class TWoauth():

    def __init__(self, consumer_key, consumer_secret, access_key, access_secret):
        self.oauth_consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
        self.oauth_token = oauth2.Token(key=access_key, secret=access_secret)
        self.signature_method_hmac_sha1 = oauth2.SignatureMethod_HMAC_SHA1()
        self.http_method = "GET"
        self.http_handler = urllib.request.HTTPHandler(debuglevel=0)
        self.https_handler = urllib.request.HTTPSHandler(debuglevel=0)

    def getTWRequest(self, url, method, parameters):
        
        req = oauth2.Request.from_consumer_and_token(self.oauth_consumer,
                                                token=self.oauth_token,
                                                http_method=self.http_method,
                                                http_url=url,
                                                parameters=parameters)
        req.sign_request(self.signature_method_hmac_sha1, self.oauth_consumer, self.oauth_token)

        if method == "POST":
            encoded_post_data = req.to_postdata()
        else:
            encoded_post_data = None

        to_url = req.to_url()

        opener = urllib.request.OpenerDirector()
        opener.add_handler(self.http_handler)
        opener.add_handler(self.https_handler)

        response = opener.open(to_url, encoded_post_data)
        
        return response

def getTwitterTwit(tweet, jsonResult):

    tweet_id = tweet['id_str']
    tweet_message = '' if 'text' not in tweet.keys() else tweet['text']    
    screen_name = '' if 'user' not in tweet.keys() else tweet['user']['screen_name']
    if 'created_at' in tweet.keys():
        # Twitter used UTC Format. EST = UTC + 9(Korean Time) Format ex: Fri Feb 10 03:57:27 +0000 2017
        tweet_published = datetime.datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        tweet_published = tweet_published + datetime.timedelta(hours=+9)
        tweet_published = tweet_published.strftime('%Y-%m-%d %H:%M:%S')   
    else:
        tweet_published = ''

    jsonResult.append({'post_id':tweet_id, 'message':tweet_message,
                    'name':screen_name, 'created_time':tweet_published})

#[CODE 2]
def fetch(filter, jsonResult):
    
    twoauth = TWoauth(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

    url = "https://stream.twitter.com/1.1/statuses/filter.json" 
    parameters = []
    parameters.append({'track', filter})
    parameters.append({'lang', 'kr'})

    try:
        f = twoauth.getTWRequest(url, "GET", parameters)
        while True:
            line = f.readline()
            if line:
                try:
                    tweet = json.loads(line.decode('utf-8'))
                    print('#####[Scrapped Time : %s]' % datetime.datetime.now())
                    print(tweet['text'])
                    getTwitterTwit(tweet, jsonResult)
                except ValueError as ve:
                    print(ve)
                except KeyError as e:
                    print(e)
            else:
                print('#')
                time.sleep(0.1)
    except KeyboardInterrupt:
        # Ctrl-C Detected
        f.close()
        with open('%s_twitter.json' % (filter), 'w', encoding='utf8') as outfile:
            retJson = json.dumps(jsonResult,
                            indent=4, sort_keys=True,
                            ensure_ascii=False)
            outfile.write(retJson)
        
        print ('%s_twitter.json SAVED' % (filter))
    
if __name__ == '__main__':
    jsonResult = []
    #filter_name = '탄핵,박근혜,광화문'
    filter_name = 'trump'
    fetch(filter_name, jsonResult)