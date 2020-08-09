import tweepy
import time
import requests
from lxml import html

auth = tweepy.OAuthHandler('zt5vtWXBmjWao6JwV2JlF57kM', 'lfz7u8OEkXcBsApGUHrv37kVe301o7dVcMx7CDudg6Wxjc3dpO')
auth.set_access_token('1285604668991660032-0yQrUjmyt4G4aT17lKtiLf5RNrpMZm',
                      'VHAPjpUjLYRBic6j1WaOkAImBwfy2dcxSNjZrWBn9QS0W')

api = tweepy.API(auth)
user = api.me()

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
    tweet = f''' Latest Covid Updates:-
Total Cases : {total}
Recovered : {recovered}
Deaths : {deaths}

Source : "https://www.worldometers.info/coronavirus/"

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
        if '#covid19' or '#coronavirus' or '#covid' or '#covidupdates' or '#covid_19' in mention.full_text.lower():
            print('found it', flush=True)
            print('responding back...', flush=True)
            tweet = covid_updates()
            api.update_status('@' + mention.user.screen_name +
                              tweet + ' Wear a mask & Stay home and Stay Safe', mention.id)
            api.retweet(mention.id)
            api.create_favorite(mention.id)


while True:
    auto()
    time.sleep(10)
    break
