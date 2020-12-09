import random
import re
import time

import requests
import tweepy
from lxml import html

CONSUMER_KEY = 'ZpCvFn5OeojLLZVCOURayaIJY'
CONSUMER_SECRET = 'VDfPkTfUZ74dGHEScdeYXJUdN2I2PVrAufLCUc0awWVggffiI6'
ACCESS_KEY = '1285604668991660032-gVTXHHRlP2r4Kt6mVgyE6TtLbGtAbD'
ACCESS_SECRET = 'xCIQTvv4ZSl1H2cdaxVK8KyUMV3P7xuEL0ouLWNuxstWp'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

FILE_NAME = 'last_seen_id.txt.txt'

s = str(random.randint(0, 1000))


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
    print('retrieving and replying to tweets...')
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(
        last_seen_id,
        tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        tweet = covid_updates()

        if '#covid_19' in mention.full_text.lower():
            print('found it')
            print('responding back...')
            api.update_status('@' + mention.user.screen_name +
                              tweet + f'Random Number:{s}', mention.id)
            api.retweet(mention.id)
            api.create_favorite(mention.id)

        else:
            arg = mention.full_text.lower()
            c = extract_country(arg)
            if country_exist(c):
                data = country_wise_data(c)
                print('found it')
                print('responding back...')
                api.update_status('@' + mention.user.screen_name +
                                  data + f'Random Number:{s}', mention.id)

                api.retweet(mention.id)
                api.create_favorite(mention.id)

            if mention.id == last_seen_id:
                time.sleep(500)


while True:
    auto()
    time.sleep(50)
