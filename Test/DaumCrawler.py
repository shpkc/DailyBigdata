
def Daum():

    print('keyword 추출 시작')

    import time
    import requests
    from bs4 import BeautifulSoup
    import lxml
    from collections import Counter
    from datetime import date, timedelta
    from joblib import Parallel, delayed
    import pandas as pd
    import re
    import os
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    # 어제 날짜와 오늘 날짜 구하기

    date_list = []

    def search_date():
        
        today = int(date.today().strftime('%Y%m%d'))
        yesterday = date.today() - timedelta(1)
        yesterday = int(yesterday.strftime('%Y%m%d'))
        
        date_list.append(yesterday)
        date_list.append(today)

    search_date()
    today = date_list[1]

    # 우리가 원하는 8개의 토픽들
    topics = ['society', 'politics', 'economic', 'foreign', 'culture',
            'entertain', 'sports', 'digital']

    def date_crawl(page):
        
        try:
            yesterday = []
            today = []
        
            url = 'http://media.daum.net/breakingnews/{}?page={}&regDate={}' \
            .format(topic, page, date)   
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            news_time = soup.find_all(class_ = 'info_time')
        
        
        
            news_time = news_time[0].text
            news_time = int(news_time[:2])
            
            # 전날 새벽6시 ~ 오후 24시까지의 데이터를 원함
            if(i==0 and news_time > 5):
                yesterday.append(page)
            
            # 당일 새벽6시 전까지의 데이터를 원함
            if(i==1 and news_time < 6):
                today.append(page)
            
            time.sleep(0.01)
        
            if(i==0):
                return yesterday
            if(i==1):
                return today
        except:
            pass

    # 1000페이지까지 크롤링하면서 우리가 원하는 시간대의 페이지를 얻는다
    # 8개 토픽들의 어제 06시 ~ 오후 24시, 오늘 06시 전까지의 페이지를 구한다
    start_time = time.time()
    total_search_page = []

    # 8개 토픽 모두 크롤링
    for topic in topics:
        
        # 어제, 오늘 순으로 크롤링
        for i, date in enumerate(date_list):
            
            
            page_info = Parallel(n_jobs=-1)(delayed(date_crawl)(page) for page in range(1,601))
            page_info = [x for x in page_info if x]
            page_info = sum(page_info, [])
            
            if i == 0:
                total_search_page.append(page_info)
            elif i == 1:
                total_search_page.append(page_info)
                
            time.sleep(0.01)
            
            
    
    # 크롤링 한번으로 키워드, 제목, url 모두 구하자
    # '추천연재'가 자동으로 크롤링되서 혼란을 주기때문에 맨마지막 2개만 뺀다

    # 크롤링 한번으로 키워드, 제목, url 모두 구하자
    # '추천연재'가 자동으로 크롤링되서 혼란을 주기때문에 맨마지막 2개만 뺀다

    def crawling_keyword_title_url(page):
        
        title_to_word = []
        title_and_address = []
        
        
        # 페이지 지정
        url = 'http://media.daum.net/breakingnews/{}?page={}&regDate={}' \
        .format(topic, page, date)   
        
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        
        if(len(soup.select('div.cont_thumb strong a')[0:15]) == 2):
                return
        
        # 제목에서 키워드을 검색
        for title in soup.select('div.cont_thumb strong a')[0:15]:
            
            
            
            # 키워드를검색하기 위해 페이지에서 제목부터 추출
            title = str(title)
            # 제목은 <a> </a>사이에 있다
            # index로 검색
            title_first_index = title.index('>')
            title_last_index = title.index('</a>')
            # 인덱스 앞뒤로 제목을 추출
            title_name = title[title_first_index+1: title_last_index]
            title_name = title_name.replace("'",'').replace('"','').replace('..','').replace('?','').replace('!','').replace(',','').replace('·','').replace('↑','')
            
            # 제목을 분석해 키워드를 분석합니다
            words = title_name.split()
            title_to_word.append(words)
                
            # 제목에 []가 들어간 것은 제목에서 빼준다
            # [르포] 혹은 [경향포토]
            if '[' and ']' in title_name:
                first_index = title_name.find('[')
                last_index = title_name.find(']')
                
                if(first_index == 0):
                    title_name = title_name[last_index+1:]
                        
                else:
                    title_name = title_name[:first_index]
                        
            
            # 기사내용을 크롤링하기 위해서 url 추출
            url_first_index = title.index('http')
            url_last_index = title.index('>')
            address = title[url_first_index:url_last_index-1]
            
            # 마지막에 DataFrame 생성을 위해 기사제목과 url은 따로 저장
            # 제목, url 순으로 list에 저장
            title_and_address.append(title_name)
            title_and_address.append(address)
            
        return title_to_word ,title_and_address
            
        time.sleep(0.1)

    # 추출한 페이지에서 뉴스 제목을 검색
    # 제목을 추출해서 단어별로 나열합니다
    title_address_list = []
    total_top10_keyword = []
    start_page = 0
    page_list = []
    title_address = []
    start_time = time.time()

    for topic in topics:
        
        
        topic_keyword = []
        
        # 디도스를 피하기 위해 time sleep
        time.sleep(3)
        
        # i는 전날이면 0, 오늘이면 1
        for i, date in enumerate(date_list):
            
            
            title_info = Parallel(n_jobs=-1)(delayed(crawling_keyword_title_url)(page) for page in total_search_page[start_page+i][:])
            title_info = [x for x in title_info if x]
            
            for p in title_info:
                
                topic_keyword.append(p[0])
                title_address_list.append(p[1])
                
        start_page+=1
        
        # 토픽별로 리스트에 통합시킨다
        topic_keyword = sum(topic_keyword, [])
        total_top10_keyword.append(topic_keyword)
        
    title_address_list = sum(title_address_list, [])

    
    keyword_ranking = []

    for i in range(len(total_top10_keyword)):
        # 1차원 리스트로 합쳐준다
        keyword_ranking.append(sum(total_top10_keyword[i], []))


    no_english_foreign_title = []
    no_english_sports_title = []

    for word in keyword_ranking[3]:
        text = re.sub('[a-zA-Z]','',word).strip()
        if(text!=''):
            no_english_foreign_title.append(text)

    for word in keyword_ranking[6]:
        text = re.sub('[a-zA-Z]','',word).strip()
        if(text!=''):
            no_english_sports_title.append(text)
            
    keyword_ranking[3] = no_english_foreign_title
    keyword_ranking[6] = no_english_sports_title

    keyword_filter = [['들어서는','피해','혐의','4월','2019','공개','사장','의원','의혹','찾은','올해','주말','부산','포항','관련','지지','호소하는','하는','후보','회장','인사하는','개최', '대표','장관', '의혹', '지원', '발표', '추진', '서울'],
                    ['기다릴','용단','뉴시스','없다','vs','호소','지지','의원','공개','평균','의혹','뒷받침','발언하는', '오늘', '정상','대표','신임'],
                    ['서울','19','찾은','상승한','피해','3월','받아','판매','인파','연속','국내','(2019','서울모터쇼)','대표이사','지부장','의혹','대비','전일','출시','상승','한국','투자','시장','5%','이벤트','기념','기업','오른','최대','영업이익','이평선','상승세','지난해', '영업익', '출시', '대비', '상승', '전일', '추가', '개최', '실시간', '분석', '매수', '종목알파고', '외국인', '수급과', '확률은', '규모', '증가', '결정', '확대', '공개', '실적', '대표', '선임', '이상', '올해', '하락', '지원', '주당', '작년', '회장', '2019','감소','만에','위한','전달','마감','강화','발표','사장','대한민국','하락한'],
                    ['19','()--','아직','읽어봤다','의혹','2019','20','2020','도착','--','만에','()'],
                    ['찾은','방문','내린','맞은','중부','곳곳','흐리고','대체로','현재','오후','대체로','4월','한때','많고','한국','2019','조금','의혹','전국','나쁨','진행','위한','발간','출시','이데일리', '공개', '나쁨', '개최', '왔어요', '대표', '서울'],
                    ['오늘','출근길)','(뮤직뱅크','2019','의혹','닿다', '눈빛','진심이','공개', '데뷔', '3월', '소녀', '1위', '이달의', '4월', '의혹', '확정', '출시', '매력', '남편'],
                    ['초대','날리는','멀리','적시타','2019','감독','한국','의혹','2020','밝히는', '각오','선수','선임','도전','공개'],
                    ['만든다','개시','시작','국내','선임','서비스','2019','개발','출시','의혹','사업', '추진', '분야', '모집', '개최','글로벌','미래','공개']]

    filter_index = 0

    for keyword in keyword_ranking:
        keyword_ranking[filter_index] = [x for x in keyword if not x in keyword_filter[filter_index]]
        filter_index+=1

    # 리스트에서 1자리 단어는 빼버림
    # []가 앞뒤로 시작하는 단어도 빼버림 ([경향포토]같은)


    total_keyword_ranking10 = []

    for i in range(len(keyword_ranking)):
        # 1위부터 보여줍니다
        ranking = 1
        
        replace = [x for x in keyword_ranking[i] if not len(x)==1 and not "[" in x and not "]" in x]
        
       
        
        temp_word = []
        
        for word, count in Counter(replace).most_common(20):
            
            # Top 20 topic
            print('가장 많이 등장한 Keyword {}위: {} / 등장 횟수 : {}'.format(ranking, word, count+1))
            temp_word.append(word)
            
            ranking+=1
            
        total_keyword_ranking10.append(temp_word[0:10])
        print('\n')


    os.mkdir('./Crawled Data/{}'.format(today))
    
    keyword_dataframe = pd.DataFrame({'Keyword':sum(total_keyword_ranking10,[])})
    keyword_dataframe.to_csv('./Crawled Data/{}/{}_Top10_keyword'.format(today, today) ,index=False)

    print('Daum News 크롤링 시작(bs4)')

    def news_company_crawl(url):
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        soup = str(soup)

        company_first_index = soup.find('property="article:txid"/>\n<meta content')
        company_last_index = soup.find('name="article:media_name')

        comapany = soup[company_first_index+41:company_last_index-2]
        
        return company

    # 뉴스 기사 크롤링

    def crawl_news_content(url):
        # 줄 별로 크롤링되니 기사들을 모두 합칠 string
        content = ''
        
        # url을 지정
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        contents = soup.find_all('p')
        
        # 맨마지막 줄은 기자 이메일이니 제외
        for line in contents[:-2]:
            line = line.text
            # 한줄 한줄 모두 더해줍니다
            content += line
        
        # 번역이 포함되어있으면 감정분석에 시간이 오래걸리므로 번역을 제외해줍니다
        if('kakao i' in content):
            # 번역이 있는 부분을 찾습니다
            translate_index = content.find('kakao i')
            # 번역이 있는 index를 찾아서 제외
            content = content[translate_index+7:]
            
        
        # 언론사 크롤링
        soup = str(soup)
        company_first_index = soup.find('property="article:txid"/>\n<meta content')
        company_last_index = soup.find('name="article:media_name')

        comapany = soup[company_first_index+41:company_last_index-2]
        
        time.sleep(0.1)
        
        return content, comapany

    topic_index = 0
    keyword_title_list = []
    total_url_list = []

    # 키워드별로 url을 추출
    for topic in topics:
        
        topic_url = []
        
        for keyword in total_keyword_ranking10[topic_index]:
            # 기사 카운트
            
            keyword_url = []
            title_list = []
            
            for i in range(len(title_address_list)-1):
                
                
                
                if keyword in title_address_list[i]:
                    
                    # 제목에 'http'가 들어가면 패스합니다
                    if('http' in title_address_list[i]):
                        continue
                    
                    keyword_url.append(title_address_list[i+1])
                    title_list.append(title_address_list[i])
                    
            topic_url.append(keyword_url)
            keyword_title_list.append(title_list)
        topic_index+=1
        
        total_url_list.append(topic_url)


    # 기사내용 크롤링

    keyword_content_list = []
    start_time = time.time()

    for total in total_url_list:
        
        # topic
        for url_list in total:
            
            content_list = []
            
            news_info = Parallel(n_jobs=-1)(delayed(crawl_news_content)(url) for url in url_list)
            
            for info in news_info:
                
                content_list.append(info[0])
                
            keyword_content_list.append(content_list)
    

    def crawl_daum_comments(url):
        
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome('/home/apostcto/ITDA/chromedriver', chrome_options=chrome_options)
        driver.get(url)

        
        try:
            elements = driver.find_element_by_class_name('alex_more')

        # 마지막 댓글까지 찾기위해 '더보기' 버튼 클릭
        # 100번이상 클릭하면 문제가 있단 뜻이니 50번넘어가면 break
            count = 0
        
            while(elements):
                try :
                    elements.click()
                    time.sleep(0.1)
                    count+=1
                
                    if (count>100):
                        break
                    
                except :
                        break
                    
        # 더보기 버튼이 없으면 현재 페이지에서 댓글 수집 
        except : 
            pass

        # 최대한 확장된 페이지에서 댓글 요소를 찾습니다
    
        comment_lists = []
        

        # 최대한 확장된 페이지에서 댓글 요소를 찾습니다
        try:
            comment_elements = driver.find_element_by_css_selector('.cmt_news').text
            count_elements = driver.find_element_by_css_selector('.cmt_news .alex_single .cmt_count').text
            count_elements = int(count_elements[3:])
        
        
            while len(comment_elements) > 30:
            # 댓글을 검색
                comment_first_index = comment_elements.find('시간전')
                comment_last_index = comment_elements.find('답글')
                comment = comment_elements[comment_first_index+4:comment_last_index-1].replace('\n','')
                
                if('댓글로그인' in comment):
                    comment = ''
                
                comment_lists.append(comment)
            
            # 더이상 댓글이 없으면 break
                if('새로고침' in comment):
                    break
        
            # 다음 댓글을 찾기위해 댓글 요소 slicing
                comment_elements = comment_elements[comment_last_index+3:]
            
            return count_elements, comment_lists, url
        
        except :
            return 0, [], []
            
    total_keyword_count = []
    total_keyword_comments_count = []
    keyword_comments_list = []
    max_url_list = []

    next = 0

    start_time = time.time()

    for total in total_url_list:
        
        # topic
        for url_list in total:
            
            keyword_count = len(url_list)
            comments_count = 0
            comments_list = []

            try:
                comments_info = Parallel(n_jobs=-1)(delayed(crawl_daum_comments)(url) for url in url_list)
                
                for p in comments_info:
                    
                    comments_count+=p[0]
                    comments_list.append(p[1])

                max_count = 0
                max_url = comments_info[0][2]
            
                for i in range(len(comments_info)):
                    if(comments_info[i][0] > max_count):
                        max_count = comments_info[i][0]
                        max_url = comments_info[i][2]
                
                total_keyword_count.append(keyword_count)
                total_keyword_comments_count.append(comments_count)
                keyword_comments_list.append(comments_list)
                max_url_list.append(max_url)

            except:

                total_keyword_count.append(keyword_count)
                total_keyword_comments_count.append(comments_count)
                keyword_comments_list.append(comments_list)
                max_url_list.append("url 없음")


            
            print('{}번째 topic의 검색횟수는 : {}'.format(next+1, total_keyword_count[next]))
            print('{}번째 topic의 총 댓글수는 : {}'.format(next+1, total_keyword_comments_count[next]))
            print('\n')
            next += 1
            
            print("걸린시간 : {}분".format(round((time.time() - start_time)/60, 1)))
            print('\n')
            time.sleep(1)
            
        if(len(total_keyword_count) > 80):
            break
       
    replace_comment_list = []

    for i in range(80):
        temp = str(keyword_comments_list[i])
        temp = temp.replace('댓글 찬성하기','').replace('댓글 비추천하기','').replace('찬성하기','').replace('비추천하기','').replace('글', '').replace('[','').replace(']','').replace("'',","").replace("\'",'').replace('\'"','')    
        replace_comment_list.append(temp)
        
    # dataframe 길이를 맞춰주기 위한 형식
        
    topics_80 = []

    for topic in topics:
        for i in range(10):
            topics_80.append(topic)
            
    keyword_80 = sum(total_keyword_ranking10, [])
    company_list = ['Daum' for _ in range(80)]

    News_dataframe = pd.DataFrame({'Topic':topics_80,
                                    'Keyword' : keyword_80,
                                    'Company' : company_list,
                                    'Title' : keyword_title_list,
                                    'Contents' : keyword_content_list,
                                    'Comments' : replace_comment_list,
                                    'KC' : total_keyword_count,
                                    'KCC' : total_keyword_comments_count})

    News_dataframe.to_csv('./Crawled Data/{}/{}_daum_news_dataframe'.format(today, today), index=False)
    News_dataframe['Contents'] = ''
    News_dataframe.to_csv('./Crawled Data/{}/{}_daum_news_dataframe(save version)'.format(today, today), index=False)
    
    url_dataframe = pd.DataFrame({'Keyword' : keyword_80,
                                  'Max_Url' : max_url_list})
    
    url_dataframe.to_csv('./Crawled Data/{}/{}_max_url'.format(today,today), index=False)