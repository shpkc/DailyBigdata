
def Instagram():

    from datetime import timedelta,date
    import pandas as pd
    from bs4 import BeautifulSoup
    import requests
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    import time
    from joblib import Parallel, delayed

    print("Instagram 크롤링 시작\n")

    topics = ['society', 'politics', 'economic', 'foreign', 'culture',
            'entertain', 'sports', 'digital']

    today = int(date.today().strftime('%Y%m%d'))
    yesterday = date.today() - timedelta(1)
    yesterday = int(yesterday.strftime('%Y%m%d'))
    keywords = pd.read_csv('./Crawled Data/{}/{}_Top10_keyword'.format(today, today))
    keywords = keywords['Keyword'].values.tolist()

    n=10
    total_keyword_ranking10 = [keywords[i:i+n] for i in range(0, len(keywords), 10)]

    # 해시태그를 검색한 페이지에서 ID(검색에 필요한 url)을 검색하는 함수

    def crawl_ID(soup):
        
        ID_list = []
        
        while len(soup) > 16000:
            ID_first_index = soup.find('shortcode')
            ID_last_index = soup.find('edge_media_to_comment')
            ID = soup[ID_first_index+12 : ID_last_index-3]
        
            # url이 아닌것은 pass
            if(len(ID)>20):
                break
        
            # 다음 url을 찾기 위해 슬라이싱
            soup = soup[ID_last_index+100:]
            # list에 추가
            ID_list.append(ID)

        # ID list 중복처리
        ID_list = set(ID_list)
        return ID_list

    # instagram 게시물에서 내용, 댓글 크롤링

    def crawl_instagram_information(id):
        
        try:
            
            
            chrome_options = webdriver.ChromeOptions()
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome('/home/apostcto/ITDA/chromedriver', chrome_options=chrome_options)
            url = 'https://www.instagram.com/p/{}'.format(id)
            driver.get(url)
            
            contents_elements = driver.find_element_by_css_selector('.C7I1f, .P9YgZ').text
            comments_elements = driver.find_elements(By.CSS_SELECTOR, '.eo2As .gElp9')[1:]
            contents_first_index = contents_elements.find('\n')
            contents_elements = contents_elements[contents_first_index:]
            contents_elements = contents_elements.replace('\n', '')
            # 페이지의 댓글을 담을 list
            url_comments_list = []
            
            # 댓글 카운트
            comment_count = 0     
        
            for comment_element in comments_elements:
    
                text = comment_element.text
                comment_index = text.find('\n')
        
                comment = text[comment_index+1:]
                
                # 댓글을 모두 담아줍니다    
                url_comments_list.append(comment)
                comment_count+=1
                
                    
                    
                # 차단을 막기위해 sleep
            driver.close()
            time.sleep(0.1)
                
            return contents_elements, url_comments_list, comment_count
        
        # 오류 발생시
        except:
            return [], [], 0

    topic_index = 0

    topic_list = []
    keyword_list = []

    keyword_content_list = []
    keyword_comments_list = []
    keyword_count_list = []
    keyword_comments_count_list = []

    start_time = time.time()

    for topic in topics:
        
        topic_comment_list = []
        
        for keyword in total_keyword_ranking10[topic_index]:
            
            content_list = []
            comment_list = []
            keyword_comment_count = 0
            
            
            url = 'https://www.instagram.com/explore/tags/{}'.format(keyword)
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            soup = str(soup)
            ID_list = crawl_ID(soup)
            
            try:
            
                parallel = Parallel(n_jobs=-1)(delayed(crawl_instagram_information)(id) for id in ID_list)
                
                # 한번 keyword 크롤리앟면 parallel에 모두 담기니
                # 각 필요한 정보를 list에 저장
                for p in parallel:
                    content_list.append(p[0])
                    comment_list.append(p[1])
                    keyword_comment_count+=p[2]
                
                
                # 각 keyword마다 카운트, 댓글 카운트
                keyword_content_list.append(content_list)
                keyword_comments_list.append(comment_list)
                keyword_count_list.append(len(ID_list))
                keyword_comments_count_list.append(keyword_comment_count)

            except:
                keyword_content_list.append(content_list)
                keyword_comments_list.append(comment_list)
                keyword_count_list.append(len(ID_list))
                keyword_comments_count_list.append(keyword_comment_count)
            
            
            
        topic_index += 1

    print("걸린시간 : {}분".format(round((time.time() - start_time)/60, 1)))
    print('\n')
            
    # dataframe을 만들기 위해 길이를 맞춰줌

    topics_80 = []
    keyword_80 = sum(total_keyword_ranking10, [])


    for topic in topics:
        for i in range(10):
            topics_80.append(topic)
            
    company_list = ['Instagram' for _ in range(80)]
    title_list = ['NaN' for _ in range(80)]

    Insta_dataframe = pd.DataFrame({'Topic':topics_80,
                                    'Keyword' : keyword_80,
                                    'Company' : company_list,
                                    'Title' : title_list,
                                    'Contents' : keyword_content_list,
                                    'Comments' : keyword_comments_list,
                                    'KC' : keyword_count_list,
                                    'KCC' : keyword_comments_count_list
                                    })
                            
    Insta_dataframe.to_csv('Crawled Data/{}/{}_instagram_dataframe'.format(today, today), index=False)
