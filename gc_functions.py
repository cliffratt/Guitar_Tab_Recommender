import requests
from bs4 import BeautifulSoup as bs
import re
import json
import numpy as np
import pandas as pd
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
sid = SentimentIntensityAnalyzer()
from selenium.webdriver import Firefox
import random
import time
import sys

def scrape_explore_page(pagenumber, category = 'hitstotal_desc'):
    """Pagenumber must be from 1 to 20. Returns a pandas dataframe"""
    url = 'https://www.ultimate-guitar.com/explore?'
    params = {'order': category,
              'page': pagenumber,
              'type[]':'Chords'}
    response = requests.get(url, params)
    soup = bs(response.content, 'html.parser')
    content = soup.text.strip().split('\n')
    res = []
    for line in content:
        line = re.sub(r'^[^a]*', '',line)
        if line.startswith('age'):
            res.append(line)
    tempstring = res[3]
    tempstring2 = tempstring.replace('age = ', '')
    tempstring3 = tempstring2[:-1]
    myjson = json.loads(tempstring3)
    templist = []
    for item in myjson['data']['data']['tabs']:
        templist.append(item)
    tempdf = pd.DataFrame(templist)
    return tempdf

def build_most_popular():
    frames = []
    for i in range(20):
        tempdf = scrape_explore_page(i+1, 'hitstotal_desc')
        frames.append(tempdf)
    tempbigtable = pd.concat(frames)
    return tempbigtable

def build_highest_rated():
    frames = []
    for i in range(20):
        tempdf = scrape_explore_page(i+1, 'rating_desc')
        frames.append(tempdf)
    tempbigtable = pd.concat(frames)
    return tempbigtable

def combine_and_remove_duplicates(df1, df2):
    combotable = pd.concat([df1, df2])
    cleancombotable = combotable.drop_duplicates(subset = 'tab_url')
    return cleancombotable

def launch_spotipy():
    """Returns an instance of spotipy"""
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    client_credentials_manager = SpotifyClientCredentials(client_id='ac2725d119934aa8a768254b50954af1', client_secret='42e73e9fc67a4a479b207778eb01d0fc')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def print_sentiments(sentences):
    """Given a list of sentences, prints sentiment information"""
    for sentence in sentences:
    print(sentence)
    ss = sid.polarity_scores(sentence)
    for k in sorted(ss):
        print('{0}: {1}, '.format(k, ss[k]), end='')
    print()

def extract_user_comments(allcomments):
    newcommentlist = []
    for i in range(len(allcomments)):
        for j in range(len(allcomments[i])):
            tempcommentlist = []
            tempstring = allcomments[i][j]
            splitstring = tempstring.split('\n',3)
            tempcomment = splitstring[0]
            newsplitstring = splitstring[2].replace('[a]', '')
            newsplitstring2 = newsplitstring.replace('  ', ' ')
            tempuser = newsplitstring2
            tempcommentlist.append(tempuser)
            tempcommentlist.append(tempcomment)
            newcommentlist.append(tempcommentlist)
    return newcommentlist