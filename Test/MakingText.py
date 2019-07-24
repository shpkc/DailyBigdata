def Text():

    import pandas as pd
    from datetime import timedelta,date 
    import os

    today = int(date.today().strftime('%Y%m%d'))
    yesterday = date.today() - timedelta(1)
    yesterday = int(yesterday.strftime('%Y%m%d'))
    month = int(date.today().strftime('%m'))
    day = int(date.today().strftime('%d'))
    os.mkdir('./Crawled Data/{}/text'.format(today))

    dataframe = pd.read_csv('./Crawled Data/{}/{}_KTR_KTS_dataframe'.format(today, today))
    dataframe = dataframe.drop_duplicates(subset = "Keyword")
    dataframe = dataframe.sort_values(by='Total_KTR', ascending=False).iloc[0:20]
    keywords = dataframe.iloc[0:10]['Keyword'].values.tolist()
    KTR = dataframe.iloc[0:10]['Total_KTR_change'].values.tolist()
    KTS = dataframe.iloc[0:10]['KTS_change'].values.tolist()
    related_keywords = dataframe['Related_Keywords'].iloc[0:10].values.tolist()
    main_text = "[📰Daily Bigdata , {}/{}]\n\n[🌏오늘의 키워드🌏]\n\n\
    1. {}\n\
    2. {}\n\
    3. {}\n\
    4. {}\n\
    5. {}\n\
    6. {}\n\
    7. {}\n\
    8. {}\n\
    9. {}\n\
    10. {}\n\n\
[💵오늘의 증시💵]\n\
코스피 2,230.50(+1.84)\n\
코스닥 743.38(-3.95)\n\
환   율 1,125.0(-1.0)\n\
\n\
📌영상으로 보고 싶으시다면?\n\
     데일리 빅데이터 유튜브!!📌\n\
    \n\n\
🚨 데일리 빅데이터를 이용한 투자 피해에는 책임을 지지 않으며 🚨\n\
        분석 자료의 해석은 개인마다 다를 수 있습니다".format(month, day,\
                keywords[0],keywords[1],keywords[2],keywords[3],\
                keywords[4],keywords[5],keywords[6],keywords[7],\
                keywords[8],keywords[9])

    file = open("./Crawled Data/{}/text/{}_main_text.txt".format(today,today), "w")
    file.write(main_text)
    file.close()



    top1_5_text = "🔎 종합 키워드 분석 TOP1~5\n\
\n\
1. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
2. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
3. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
4. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
5. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
📌영상으로 보고 싶으시다면?\n\
    데일리 빅데이터 유튜브!!📌".format(keywords[0], KTR[0], KTS[0], related_keywords[0],\
                  keywords[1], KTR[1], KTS[1], related_keywords[1],\
                  keywords[2], KTR[2], KTS[2], related_keywords[2],\
                  keywords[3], KTR[3], KTS[3], related_keywords[3],\
                  keywords[4], KTR[4], KTS[4], related_keywords[4])

    file = open("./Crawled Data/{}/text/{}_top1_5_text.txt".format(today,today), "w")
    file.write(top1_5_text)
    file.close()


    url_dataframe = pd.read_csv('./Crawled Data/{}/{}_max_url'.format(today, today))
    max_url = ''
    for keyword in keywords:
        for i in range(80):
            if keyword == url_dataframe.iloc[i]['Keyword']:
                max_url = max_url+keyword+' '+url_dataframe.iloc[i]['Max_Url']+'\n'
                break
    file = open("./Crawled Data/{}/text/{}_max_url.txt".format(today,today), "w")
    file.write(max_url)
    file.close()


    top6_10_text = "🔎 종합 키워드 분석 TOP1~5\n\
\n\
6. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
7. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
8. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
9. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
10. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
📌영상으로 보고 싶으시다면?\n\
    데일리 빅데이터 유튜브!!📌".format(keywords[5], KTR[5], KTS[5], related_keywords[5],\
                  keywords[6], KTR[6], KTS[6], related_keywords[6],\
                  keywords[7], KTR[7], KTS[7], related_keywords[7],\
                  keywords[8], KTR[8], KTS[8], related_keywords[8],\
                  keywords[9], KTR[9], KTS[9], related_keywords[9])

    file = open("./Crawled Data/{}/text/{}_top6_10_text.txt".format(today,today), "w")
    file.write(top6_10_text)
    file.close()


    today_KTR_KTS = pd.read_csv('./Crawled Data/{}/{}_KTR_KTS_dataframe'.format(today, today))
    topics = ['society', 'politics', 'economic', 'foreign', 'culture',
                'entertain', 'sports', 'digital']
    topics_emoji = ['🌉','⚖','💲','🌏','🎼','🎤','⚽','💻']
    topics_kr = ['사회', '정치', '경제', '국제', '문화', '연예', '스포츠', 'IT']

    kr_index = 0

    for topic in topics:

        dataframe = today_KTR_KTS[today_KTR_KTS['Topic'] == topic].sort_values(by='Total_KTR', ascending=False)
        keywords = dataframe.iloc[0:10]['Keyword'].values.tolist()
        KTR = dataframe.iloc[0:10]['Total_KTR_change'].values.tolist()
        KTS = dataframe.iloc[0:10]['KTS_change'].values.tolist()
        related_keywords = dataframe['Related_Keywords'].iloc[0:10].values.tolist()

                
        text = "{} {} 키워드\n\n\
    1. {}\n\
    2. {}\n\
    3. {}\n\
    4. {}\n\
    5. {}\n\
    6. {}\n\
    7. {}\n\
    8. {}\n\
    9. {}\n\
    10. {}\n\
\n\
[🔎키워드 분석🔍]\n\n\
1. {}\n\
관심도 * : {}\n\
감정도 : {}\n\
{}\n\
\n\
2. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
3. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
4. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
5. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
6. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
7. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
8. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
9. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
10. {}\n\
관심도 : {}\n\
감정도 : {}\n\
{}\n\
\n\
* = 당일 평균 키워드 대비 백분율\n\
\n\
📌영상으로 보고 싶으시다면?\n\
    데일리 빅데이터 유튜브!!📌".format(topics_emoji[kr_index], topics_kr[kr_index],\
                keywords[0],keywords[1],keywords[2],keywords[3],\
                keywords[4],keywords[5],keywords[6],keywords[7],\
                keywords[8],keywords[9],\
                keywords[0],KTR[0],KTS[0],related_keywords[0],\
                keywords[1],KTR[1],KTS[1],related_keywords[1],\
                keywords[2],KTR[2],KTS[2],related_keywords[2],\
                keywords[3],KTR[3],KTS[3],related_keywords[3],\
                keywords[4],KTR[4],KTS[4],related_keywords[4],\
                keywords[5],KTR[5],KTS[5],related_keywords[5],\
                keywords[6],KTR[6],KTS[6],related_keywords[6],\
                keywords[7],KTR[7],KTS[7],related_keywords[7],\
                keywords[8],KTR[8],KTS[8],related_keywords[8],\
                keywords[9],KTR[9],KTS[9],related_keywords[9])
        
        kr_index+=1

        file = open("./Crawled Data/{}/text/{}_{}_text.txt".format(today,today, topic), "w")
        file.write(text)
        file.close()
    print("모든 작업 완료")