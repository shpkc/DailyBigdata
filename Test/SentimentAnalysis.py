
def LSTM():
    
    print('Sentiment Analysis 시작')

    import json
    import os
    from pprint import pprint
    from konlpy.tag import Okt
    import nltk
    import numpy as np
    import pandas as pd
    import time
    from keras.datasets import imdb
    from keras.models import Sequential
    from keras.layers import Dense, LSTM, Embedding
    from keras.preprocessing import sequence
    from keras.callbacks import EarlyStopping
    from keras.models import load_model
    from datetime import timedelta,date        
    
    def read_data(filename):
        with open(filename, 'r') as f:
            # tab 별로 자른다
            data = [line.split('\t') for line in f.read().splitlines()]
            # txt 파일의 헤더(id document label)는 제외하기
            data = data[1:]
        return data

    train_data = read_data('ratings_train.txt')
    test_data = read_data('ratings_test.txt')

    okt = Okt()

    def tokenize(doc):
        # 토큰과 근어 사이에 '/'로 구부해줍니다
        # norm은 정규화, stem은 근어로 표시하기를 나타냄
        return ['/'.join(t) for t in okt.pos(doc, norm=True, stem=True)]

    # 매번 반복하지 않기 위해 json파일이 있으면 읽어서 사용
    if os.path.isfile('train_docs.json'):
        with open('train_docs.json') as f:
            train_docs = json.load(f)
        with open('test_docs.json') as f:
            test_docs = json.load(f)
    else:
        # row[1]에 리뷰가, row[2]에 부정or긍정이 담겨있음
        train_docs = [(tokenize(row[1]), row[2]) for row in train_data]
        test_docs = [(tokenize(row[1]), row[2]) for row in test_data]
        # JSON 파일로 저장
        with open('train_docs.json', 'w', encoding="utf-8") as make_file:
            json.dump(train_docs, make_file, ensure_ascii=False, indent="\t")
        with open('test_docs.json', 'w', encoding="utf-8") as make_file:
            json.dump(test_docs, make_file, ensure_ascii=False, indent="\t")

    tokens = [t for d in train_docs for t in d[0]]

    text = nltk.Text(tokens, name='NMSC')



    # 모든 문장을 학습할 순 없으니 가장 많이 등장하는 2500개의 토큰을 사용해서 벡터화
    # RAM이 높다면 10000까지 해봅시다
    selected_words = [f[0] for f in text.vocab().most_common(3000)]

    # selected_words 안에 있는 단어들이 doc안에 있는지 확인해서 반환
    # 문서집합에서 단어 토큰을 생성하고 각 단어의 수를 세어 BOW 인코딩한 벡터를 만듭니다
    # BOW(Back Of Words)
    def term_frequency(doc):
        return [doc.count(word) for word in selected_words]

    # token_list : 0 or 1(긍정,부정)으로 이루어져있으므로 token_list만 확인(d, _)
    # train_docs 안에 있는 toekn중 selected_words에 들어있는 단어만 포함
    # train_docs는 2차원 list들([[영화 리뷰], 긍정or부정])로 구성된 3차원 list
    # train_x는 0과 1로 이루어진 5천개의 list가 15만개 존재(2차원 list)
    train_x = [term_frequency(d) for d, _ in train_docs]
    test_x = [term_frequency(d) for d, _ in test_docs]
    train_y = [c for _, c in train_docs]
    test_y = [c for _, c in test_docs]

    # 데이터가 문자열이니 input을 위해 float으로 바꿔줍니다
    # 15만개의 데이터가 각각 2500개의 0과 1로 존재

    x_train = np.asarray(train_x).astype('float32')
    x_test = np.asarray(test_x).astype('float32')

    y_train = np.asarray(train_y).astype('float32')
    y_test = np.asarray(test_y).astype('float32')

    # LSTM은 3차원 리스트만 input으로 받으니 3차원으로 reshape 해줍니다
    # [샘플 수, 타임스텝 수, 속성 수]로 구성됩니다
    # 타임스텝이란 하나의 샘플에 포함된 시퀀스 개수(여기선 리뷰 글 하나)
    # embedding 기능을 사용하면 자동으로 변환되지만 학습이 너무 느려져 직접 변환해줍니다

    X_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))
    X_test = np.reshape(x_test, (x_test.shape[0], 1, x_train.shape[1]))


    model = Sequential()
    model.add(LSTM(100))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                optimizer='adam',
                metrics=['accuracy'])

    # 과적합을 방지하기 위해 과적합이 진행되면 바로 EarlyStopping
    early_stopping = EarlyStopping()

    model.fit(X_train, y_train, validation_data=(X_test, y_test), 
            epochs=100, batch_size=25, callbacks=[early_stopping])

    scores = model.evaluate(X_test, y_test, verbose=0)

    model.save('Sentiment Analysis.h5')
    
    
    # 문장에서 이모티콘 처리를 해줍니다
    emoji = pd.read_csv('Emoji.csv')

    # emoji 딕셔너리로 만들어서 {emoji : emoji_sentiment}로 만들기
    emoji_list = emoji['Emoji'].tolist()
    emoji_neg = emoji['Negative'].tolist()
    emoji_pos = emoji['Positive'].tolist()

    emoji.head(20)

    # 이모티콘 딕셔너리를 만들어 {이모티콘 : 감정도} 형식으로 짝을 맞춰줍니다
    emoji_dictionary = {}

    for i in range(len(emoji_list)):
        
        # 이모티콘 긍정이 부정보다 높으면 양수
        if(emoji_pos[i]-emoji_neg[i]>0):
            emoji_sentiment = emoji_pos[i]- emoji_neg[i]
        # 이모티콘 부정이 긍정보다 높으면 음수
        else:
            emoji_sentiment = emoji_pos[i]- emoji_neg[i]
        
        # 각각 scale이 다르므로 소수점자리를 맞춰줍니다
        if(abs(emoji_sentiment)>=1000):
            emoji_sentiment/=1000000
        elif(abs(emoji_sentiment)>=100):
            emoji_sentiment/=100000
        elif(abs(emoji_sentiment)>=10):
            emoji_sentiment/=10000
        else:
            emoji_sentiment/=1000
        
        # 딕셔너리에 {이모티콘 : 감정도}로 추가
        emoji_dictionary[emoji_list[i]] = emoji_sentiment

    def predict_sentiment_with_emoji(word):
        
        try:

            # 문장을 token화 시키고
            token = tokenize(word)
            # 가장많이 등장하는 단어와 토큰과 비교를하고
            tf = term_frequency(token)
            # 문장을 float형식으로 바꿔줍니다
            data = np.expand_dims(np.asarray(tf).astype('float32'), axis=0)
            # LSTM에 맞게 3차원 배열로 바꿔줍니다
            data = np.reshape(data, (data.shape[0], 1, data.shape[1]))
            # 예전에 학습한 LSTM모델을 불러옵니다
            score = float(model.predict(data))
        
            # 문장에 이모티콘이 포함되어 있으면 이모티콘의 sentiment만큼 가중치를 줍니다
            for emoji in emoji_dictionary:
                if emoji in word:
                    score += emoji_dictionary[emoji]
            
            # 소수 5자리까지만 반환
            return round(score, 5)
        
        except:
            
            return 0.5


    topics = ['society', 'politics', 'economic', 'foreign', 'culture',
            'entertain', 'sports', 'digital']

    today = int(date.today().strftime('%Y%m%d'))
    yesterday = date.today() - timedelta(1)
    yesterday = int(yesterday.strftime('%Y%m%d'))
    keywords = pd.read_csv('./Crawled Data/{}/{}_Top10_keyword'.format(today, today))
    keywords = keywords['Keyword'].values.tolist()

    n=10
    total_keyword_ranking10 = [keywords[i:i+n] for i in range(0, len(keywords), 10)]

    insta = pd.read_csv('./Crawled Data/{}/{}_instagram_dataframe'.format(today,today))
    daum_news = pd.read_csv('./Crawled Data/{}/{}_daum_news_dataframe'.format(today,today))
    twitter = pd.read_csv('./Crawled Data/{}/{}_tweet_dataframe'.format(today,today))
    youtube = pd.read_csv('./Crawled Data/{}/{}_youtube_dataframe'.format(today,today))

    # 빈 dataframe을 만들어줘서 차곡차곡 넣는다

    today_dataframe = pd.DataFrame(columns=['Topic', 'Keyword', 'Company', 'Title', 'Contents', 'Comments', 'KC', 'KCC'])

    # daum, youtube, insta, twitter 순으로 넣어준다

    index = 0

    for i in range(80):
        today_dataframe.loc[index] = daum_news.loc[i]
        index += 1
        today_dataframe.loc[index] = youtube.loc[i]
        index += 1
        today_dataframe.loc[index] = insta.loc[i]
        index += 1
        today_dataframe.loc[index] = twitter.loc[i]
        index += 1


    # Keyword Total Ratio 추가
    # Total KTR, Topic KTR 따로

    Total_KTR_list = []
    Topic_KTR_list = []
    Topic_KTR_dataframe = []
    KTR_list = []
    total_count_list = []
    Topic_mean_list = []

    total_count = 0

    # Total KTR을 구하기 위해 평균을 구한다

    for i in range(0,320,4):
        count = 0
        for j in range(4):
            count += today_dataframe.iloc[i+j]['KC']
            count += today_dataframe.iloc[i+j]['KCC']
        total_count_list.append(count)
        total_count+= count
        
    mean_ratio = total_count/80

    # 평균대비 Keyword Total Ratio

    for i in range(80):
        total_KTR = round((total_count_list[i]/mean_ratio),2)
        Total_KTR_list.append(int(total_KTR*100))
        for j in range(4):
            KTR = round((total_count_list[i]/mean_ratio),2)
            KTR_list.append(str(int(KTR * 100))+'%')

    # Topic별로 KTR을 구하기 위해 Topic별로 평균을 구한다

    for i in range(8):
        count=0
        for j in range(10):
            count+=total_count_list[10*i+j]
            
        Topic_mean_list.append(count/10)

        
    for i in range(8):
        for j in range(10):
            topic_ktr = round((total_count_list[10*i+j] / Topic_mean_list[i]),2)
            Topic_KTR_list.append(int(topic_ktr*100))

    time.sleep(5)

    print("감정분석을 시작합니다")

    # Keyword Total Sentiment 추가

    sentiment_list = []
    start_time = time.time()

    for i in range(320):
        
        title = str(today_dataframe.iloc[i]['Title'])
        content = str(today_dataframe.iloc[i]['Contents'])
        comment = str(today_dataframe.iloc[i]['Comments'])
        
        title_content_sentiment = predict_sentiment_with_emoji(title+content)
        comment_sentiment = predict_sentiment_with_emoji(comment)
        sentiment = round((title_content_sentiment + comment_sentiment)/2,2)
        sentiment_list.append(int(sentiment*100))

    print("걸린시간 : {}분".format(round((time.time() - start_time)/60, 1)))
    print('\n')
    
    # Keyword Total Sentiment
    # Daum News 50%, Youtube 35%, Instagram 5%, Twitter 15%의 가중치 

    today_dataframe_KTS = []
    Total_KTS_list = []

    for i in range(0,320,4):
        KTS = 0
        for j in range(4):
            if(j % 4==0):
                KTS += 0.5 * sentiment_list[i+j]
            elif(j % 4==1):
                KTS += 0.35 * sentiment_list[i+j]
            elif(j % 4==2):
                KTS += 0.05 * sentiment_list[i+j]
            else:
                KTS += 0.15 * sentiment_list[i+j]
        
        Total_KTS_list.append(int(KTS))

    topic_list = daum_news['Topic'].values.tolist()
    keyword_list = daum_news['Keyword'].values.tolist()

    today_KTR_KTS = pd.DataFrame({'Topic':topic_list,
                                    'Keyword':keyword_list,
                                    'Total_KTR':Total_KTR_list,
                                    'Topic_KTR':Topic_KTR_list,
                                    'KTS':Total_KTS_list})

    today_KTR_KTS.to_csv('./Crawled Data/{}/{}_KTR_KTS_dataframe'.format(today, today), index=False)
    


    # 연관검색어 검색
    keywords = pd.read_csv('./Crawled Data/{}/{}_Top10_keyword'.format(today, today))
    keyword_list = keywords['Keyword'].values.tolist()
    top5_topic = []

    # pytrend는 keyword를 str이 아니라 list로 받으므로
    # top5 topic을 모두 2차원 list로 설정

    for i in range(8):
        for j in range(10):
            top5_topic.append([keyword_list[10*i+j]])

    # top5 topic의 연관검색어 추출

    print("연관검색어 검색 시작")
    from pytrends.request import TrendReq

    top3_related_keyword = []
    top3_related_value = []

    pytrends = TrendReq(hl='ko')

    for i in range(len(top5_topic)):

        # 시간설정은 지난 하루동안, 지역은 한국설정
        # 'rising'부분이 급상승 키워드 부분입니다(가중치도 함께 출력)

        try:
            pytrends.build_payload(top5_topic[i], geo = 'KR', timeframe='now 1-d')
            queries = pytrends.related_queries()
            dataframe = queries[top5_topic[i][0]]['rising']

            top3_related_keyword.append(dataframe['query'].values.tolist()[0:3])
            top3_related_value.append(dataframe['value'].values.tolist()[0:3])

        except:
            top3_related_keyword.append('[없음]')
            top3_related_value.append('[없음]')
            
    for i in range(80):
        
        if top3_related_keyword[i] == '[없음]':
            top3_related_keyword[i] = '#없음'
        else:
            for j in range(len(top3_related_keyword[i])):
                top3_related_keyword[i][j] = '#'+top3_related_keyword[i][j]
                if (" ") in top3_related_keyword[i][j]:
                    top3_related_keyword[i][j] = top3_related_keyword[i][j].replace(" ", "")


    for i in range(len(top3_related_keyword)):
        if(type(top3_related_keyword[i]) == list):
            top3_related_keyword[i] = (' ').join(top3_related_keyword[i])

    # today_KTR_KTS dataframe

    topic_list = daum_news['Topic'].values.tolist()
    keyword_list = daum_news['Keyword'].values.tolist()

    today_KTR_KTS = pd.DataFrame({'Topic':topic_list,
                                'Keyword':keyword_list,
                                'Total_KTR':Total_KTR_list,
                                'Topic_KTR':Topic_KTR_list,
                                'KTS':Total_KTS_list,
                                'Related_Keywords':top3_related_keyword})

    today_KTR_KTS.to_csv('./Crawled Data/{}/{}_KTR_KTS_dataframe'.format(today, today), index=False)

    # 어제와 오늘 중복된 Keyword가 있으면 변화량을 측정하기 위해
    # 어제의 csv파일을 불러온다

    yesterday_KTR_KTS = pd.read_csv('./Crawled Data/{}/{}_KTR_KTS_dataframe'.format(yesterday, yesterday))

    compare_Total_KTR_list = Total_KTR_list
    compare_KTS_list = Total_KTS_list

    for i in range(8):

        for j in range(10):

            keyword = today_KTR_KTS.iloc[10*i+j]['Keyword']

            for k in range(10):

                if keyword == yesterday_KTR_KTS.iloc[10*i+k]['Keyword']:

                    Total_KTR_change = int(today_KTR_KTS.iloc[10*i+j]['Total_KTR']) - int(yesterday_KTR_KTS.iloc[10*i+k]['Total_KTR'])
                    KTR_change = str(abs(Total_KTR_change))
                    
                    if(Total_KTR_change < 0):
                        compare_Total_KTR_list[10*i+j] = (str(today_KTR_KTS.iloc[10*i+j]['Total_KTR'])+'% ('+KTR_change+'🔻)')
                    else:
                        compare_Total_KTR_list[10*i+j] = (str(today_KTR_KTS.iloc[10*i+j]['Total_KTR'])+'% ('+KTR_change+'🔺)')

                    Total_KTS_change = int(today_KTR_KTS.iloc[10*i+j]['KTS']) - int(yesterday_KTR_KTS.iloc[10*i+k]['KTS'])
                    KTS_change = str(abs(Total_KTS_change))
                    
                    if(Total_KTS_change < 0):
                        compare_KTS_list[10*i+j] = (str(today_KTR_KTS.iloc[10*i+j]['KTS'])+'% ('+KTS_change+'🔻)')
                    else:
                        compare_KTS_list[10*i+j] = (str(today_KTR_KTS.iloc[10*i+j]['KTS'])+'% ('+KTS_change+'🔺)')
    # %를 붙여줍니다
    for i in range(80):
        if ('%' not in str(compare_Total_KTR_list[i])):
            compare_Total_KTR_list[i] = str(compare_Total_KTR_list[i]) + '%'
        if ('%' not in str(compare_KTS_list[i])):
            compare_KTS_list[i] = str(compare_KTS_list[i]) + '%'

    

    today_KTR_KTS['Total_KTR_change'] = compare_Total_KTR_list
    today_KTR_KTS['KTS_change'] = compare_KTS_list

    today_KTR_KTS.to_csv('./Crawled Data/{}/{}_KTR_KTS_dataframe'.format(today, today), index=False)
