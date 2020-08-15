import tweepy
import time
import requests
from lxml import html

CONSUMER_KEY = 'A'
CONSUMER_SECRET = 'b'
ACCESS_KEY = 'c'
ACCESS_SECRET = 'd'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

FILE_NAME = 'last_seen_id.txt.txt'


def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def covid_updates():
    response = requests.get('https://www.worldometers.info/coronavirus/')
    doc = html.fromstring(response.content)
    total, deaths, recovered = doc.xpath('//div[@class="maincounter-number"]/span/text()')
    active_cases, closed_cases = doc.xpath('//div[@class="panel_front"]//div[@class="number-table-main"]/text()')
    tweet = f'''  Latest Covid Updates:-
                   Total Cases : {total}
Active Cases :{active_cases}    Closed Cases :{closed_cases}
                      Deaths : {deaths}
                  Recovered : {recovered} 

'''
    return tweet


def auto():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(
        last_seen_id,
        tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        tweet = covid_updates()
        if '#covid19' or '#coronavirus' or '#covid' or '#covidupdates' or '#covid_19' in mention.full_text.lower():
            print('found it', flush=True)
            print('responding back...', flush=True)
            api.update_status('@' + mention.user.screen_name +
                              tweet + "You see that ! So, Please wear a mask and stay safe.", mention.id)
            api.retweet(mention.id)
            api.create_favorite(mention.id)


while True:
    a_p_i = tweepy.API(auth)
    auto()
    time.sleep(10)
