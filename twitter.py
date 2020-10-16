import re
import time
from os import environ

import requests
import tweepy
from lxml import html

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']

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


def country_exist(argument):
    response = requests.get(f'https://www.worldometers.info/coronavirus/')
    doc = html.fromstring(response.content)
    con_name = doc.xpath('//a[@class="mt_a"]/text()')
    county = str(list(dict.fromkeys(con_name))).lower()
    if argument in county:
        return True


def extract_country(string):
    x = re.search(r"[@].*#", string)
    text = x.group()
    new = string.replace(text, '').strip().lower()
    return new


def country_wise_data(ctry):
    if country_exist(ctry):
        response = requests.get(f'https://www.worldometers.info/coronavirus/country/{ctry}')
        doc = html.fromstring(response.content)
        total, deaths, recovered = doc.xpath('//div[@class="maincounter-number"]/span/text()')
        tweet = f'''  Latest Covid Updates:-
                           Total Cases : {total}
                              Deaths : {deaths}
                          Recovered : {recovered} 
                '''
        return tweet
    else:
        print("Unable to find a unique country name!")


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
        if '#covid19' in mention.full_text.lower():
            print('found it', flush=True)
            print('responding back...', flush=True)
            api.update_status('@' + mention.user.screen_name +
                              tweet + "You see that ! So, Please wear a mask and stay safe.", mention.id)
            api.retweet(mention.id)
            api.create_favorite(mention.id)
        else:
            arg = mention.full_text.lower()
            c = extract_country(arg)
            if country_exist(c):
                data = country_wise_data(c)
                print('found it', flush=True)
                print('responding back...', flush=True)

                api.update_status('@' + mention.user.screen_name +
                                  data + "You see that ! So, Please wear a mask and stay safe.", mention.id)

                api.retweet(mention.id)

                api.create_favorite(mention.id)


while True:
    a_p_i = tweepy.API(auth)
    auto()
    time.sleep(15)
