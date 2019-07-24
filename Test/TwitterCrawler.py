
def Twitter():

    print('Twitter 크롤링 시작')

    import os
    import sys
    import urllib.request
    import json
    from textblob import TextBlob
    import nltk   
    import tweepy
    import config
    from textblob import TextBlob
    from textblob.sentiments import NaiveBayesAnalyzer
    import re
    import time
    from datetime import timedelta,date
    import pandas as pd
    from joblib import Parallel, delayed
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('movie_reviews')


    
    # 트위터
    # 컨슈머키 
    # KqposylasMpKJvrKcUt5u1qf2
    # MyMrf4mbci7eWewZ0cgIV3rQKteek8MEuCURh5M6Sr0mc3fYoi
    # consumer_key = config.consumer_key
    # consumer_secret = config.consumer_secret

    consumer_key = 'KqposylasMpKJvrKcUt5u1qf2'
    consumer_secret ='MyMrf4mbci7eWewZ0cgIV3rQKteek8MEuCURh5M6Sr0mc3fYoi'

    # 엑세스토큰
    # 413828241-YD0khaiuEUUK6BQGRevzNU2j1nZBqOXTPysDLKkQ
    # oxPsaULAKkTPUjwtdS3JYsBSvZ5WNPYQoIcKR0W1i7the
    # access_token = config.access_token
    # access_token_secret = config.access_token_secret

    access_token = '413828241-YD0khaiuEUUK6BQGRevzNU2j1nZBqOXTPysDLKkQ'
    access_token_secret = 'oxPsaULAKkTPUjwtdS3JYsBSvZ5WNPYQoIcKR0W1i7the'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    topics = ['society', 'politics', 'economic', 'foreign', 'culture',
            'entertain', 'sports', 'digital']

    today = int(date.today().strftime('%Y%m%d'))
    yesterday = date.today() - timedelta(1)
    yesterday = int(yesterday.strftime('%Y%m%d'))
    keywords = pd.read_csv('./Crawled Data/{}/{}_Top10_keyword'.format(today, today))
    keywords = keywords['Keyword'].values.tolist()

    n=10
    total_keyword_ranking10 = [keywords[i:i+n] for i in range(0, len(keywords), 10)]

    def tweet_crawl(keyword):
        
        tweet_list = []
        tweet_news_list = []
        
        tweet_count = 0
        tweet_news_count = 0
        
        public_tweets_ko = api.search(keyword,lang='ko',count='100')
        
        for tweet in public_tweets_ko:
            
            tweet = tweet.text
                
            # 트위터에서 'RT'라 적힌 부분은 지워줍니다
            if 'RT' in tweet:
                replace_index = tweet.find(':')
                tweet = tweet[replace_index+2:]
            
            if 'http' in tweet:
                tweet_news_list.append(tweet)
                tweet_news_count += 1
                    
            else:
                tweet_list.append(tweet)
                tweet_count += 1
                
            time.sleep(1)
        
        return tweet_list, tweet_news_list, tweet_count, tweet_news_count



    keyword_tweet_list = []
    keyword_tweet_news_list = []
    keyword_tweet_count = []
    keyword_tweet_news_count = []
    keyword_tweet_count_after30 = []
    keyword_tweet_news_count_after30 = []

    for i in range(2):
        
        topic_index = 0
        
        start_time = time.time()
        
        for topic in topics:
        
            print('{}분야를 검색합니다'.format(topic))
            # top10 키워드별로 검색
                
            tweet_info = Parallel(n_jobs=-1)(delayed(tweet_crawl)(keyword) for keyword in total_keyword_ranking10[topic_index])
                
            for tweet in tweet_info:
                    
                keyword_tweet_list.append(tweet[0])
                keyword_tweet_news_list.append(tweet[1])
                
                if(i==1):
                    keyword_tweet_count_after30.append(tweet[2])
                    keyword_tweet_news_count_after30.append(tweet[3])
                else:
                    keyword_tweet_count.append(tweet[2])
                    keyword_tweet_news_count.append(tweet[3])
                
            
            time.sleep(5)
            topic_index+=1
        
        print('\n')
        print("총 걸린시간 : {}분".format(round((time.time() - start_time)/60, 1)))
        print('\n')
        
        if(i == 0):
            time.sleep(1800)
            print('30분 sleep\n')

    keyword_tweet_list = keyword_tweet_list[0:80]
    keyword_tweet_news_list = keyword_tweet_news_list[0:80]

    # 30분 sleep 후 크롤링을 통해 트윗 추정량 측정

    estimated_tweet = []
    estimated_tweet_news = []

    for i in range(len(keyword_tweet_count)):
        try:
            tweet_change = 48 * (keyword_tweet_count_after30[i] / (keyword_tweet_count[i]+keyword_tweet_count_after30[i]))
            estimated_tweet.append(round(keyword_tweet_count_after30[i] * tweet_change))
        except:
            estimated_tweet.append(0)
    for i in range(len(keyword_tweet_news_count)):
        try:
            tweet_change = 48 * (keyword_tweet_news_count[i] / (keyword_tweet_news_count[i]+keyword_tweet_news_count_after30[i]))
            estimated_tweet_news.append(round(keyword_tweet_news_count_after30[i] * tweet_change))
        except:
            estimated_tweet_news.append(0)

    # dataframe 길이를 맞추기 위한 형식

    topics_80 = []
    keyword_80 = sum(total_keyword_ranking10, [])


    for topic in topics:
        for i in range(10):
            topics_80.append(topic)
            
    company_list = ['Twitter' for _ in range(80)]
    title_list = ['NaN' for _ in range(80)]

    Tweet_dataframe = pd.DataFrame({'Topic':topics_80,
                                    'Keyword' : keyword_80,
                                    'Company' : company_list,
                                    'Title' : title_list,
                                    'Contents' : keyword_tweet_list,
                                    'Comments' : keyword_tweet_news_list,
                                    'KC' : estimated_tweet,
                                    'KCC' : estimated_tweet_news
                                    })


    Tweet_dataframe.to_csv('Crawled Data/{}/{}_tweet_dataframe'.format(today, today), index=False)
