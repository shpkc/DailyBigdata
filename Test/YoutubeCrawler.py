def Youtube():

    print('Youtube 크롤링 시작')

    from datetime import date, timedelta
    import pandas as pd
    from apiclient.discovery import build
    from apiclient.errors import HttpError
    from oauth2client.tools import argparser
    import time
    from joblib import Parallel, delayed

    topics = ['society', 'politics', 'economic', 'foreign', 'culture',
            'entertain', 'sports', 'digital']

    today = int(date.today().strftime('%Y%m%d'))
    yesterday = date.today() - timedelta(1)
    yesterday = int(yesterday.strftime('%Y%m%d'))

    keywords = pd.read_csv('./Crawled Data/{}/{}_Top10_keyword'.format(today, today))
    keywords = keywords['Keyword'].values.tolist()

    n=10
    total_keyword_ranking10 = [keywords[i:i+n] for i in range(0, len(keywords), 10)]

    DEVELOPER_KEY1 = 'AIzaSyD_EgMkZTUp5-RaHLB8n3zHWx1iybXWhig'
    DEVELOPER_KEY2 = 'AIzaSyD59L1--kJqRGIw0iT3ze66zLLN1dd3bDQ'
    DEVELOPER_KEY3 = 'AIzaSyArZ5WdVIiBMcH3Rujsnojbk0MzilL_RpA'
    DEVELOPER_KEY4 = 'AIzaSyBBGqepG1SnAPb5vyH1WBVqTwufwPF0_OM'
    DEVELOPER_KEY5 = 'AIzaSyALIHTpYjrtQl7rZ2pdqGntPbrB5CZaMh8'
    DEVELOPER_KEY6 = 'AIzaSyDWGznN5I-8iocC4h6mxYCrua4JuhPDXXE'

    def youtube_cralwer(keyword):
        
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

            # q에 검색하고 싶은 keyword를 입력합니다
            # 국가는 한국으로 제한합니다
        search_response = youtube.search().list(
                q=keyword,
                part="id,snippet",
                maxResults=50,
                type='video',
                regionCode='KR'
            ).execute()

            # videoID를 담을 list
        video_id = []
        title_list = []
        content_list = []
            
            # 검색결과에서 url에 필요한 videoID를 가져옵니다
        for search_result in search_response.get("items", []):
            id = search_result['id']['videoId']
            title = search_result['snippet']['title']
            content = search_result['snippet']['description']
            title_list.append(title)
            content_list.append(content)
            video_id.append(id)
                
        time.sleep(2)
            
            # 검색한 동영상에서 댓글을 가져옵니다    
            
        comment_list = []
            
        for id in video_id:
                
            try:
                youtube_comment = youtube.commentThreads().list(
                                part="snippet",
                                videoId=id,
                                textFormat = 'plainText',
                                ).execute()
                    
                for item in youtube_comment['items']:
                    comment = item["snippet"]["topLevelComment"]
                    text = comment["snippet"]["textDisplay"]
                    text = text.replace('\n', '')

                    comment_list.append(text)
                        # 댓글 count
                    
                    
                time.sleep(2)
                
            except :
                comment_list.append('')
                time.sleep(2)
                
        return title_list, comment_list, content_list, len(video_id), len(comment_list)

    keyword_title_list = []
    keyword_comment_list = []
    keyword_content_list = []
    keyword_count_list = []
    keyword_commment_count_list = []


    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    topic_index = 0

    start_time = time.time()

    # 토픽별로 검색
    for topic in topics:
        
        
        # api key를 3개 사용해서 나눠서 검색
        if(topics.index(topic) <= 2):
            DEVELOPER_KEY = DEVELOPER_KEY4
        elif(topics.index(topic) <= 5):
            DEVELOPER_KEY = DEVELOPER_KEY5
        else:
            DEVELOPER_KEY = DEVELOPER_KEY6
        
        
        # top10 키워드별로 검색
        
        youtube_info = Parallel(n_jobs=-1)(delayed(youtube_cralwer)(keyword) for keyword in total_keyword_ranking10[topic_index])
        
        for youtube in youtube_info:
            
            keyword_title_list.append(youtube[0])
            keyword_comment_list.append(youtube[1])
            keyword_content_list.append(youtube[2])
            keyword_count_list.append(youtube[3])
            keyword_commment_count_list.append(youtube[4])
            
        time.sleep(5)
        topic_index+=1
        
    
    topics_80 = []
    keyword_80 = sum(total_keyword_ranking10, [])
    keyword_comment_ratio = []

    for topic in topics:
        for i in range(10):
            topics_80.append(topic)
            

    company_list = ['Youtube' for _ in range(80)]

    youtube_dataframe = pd.DataFrame({'Topic':topics_80,
                                    'Keyword':keyword_80,
                                    'Company':company_list,
                                    'Title':keyword_title_list,
                                    'Contents':keyword_content_list,
                                    'Comments':keyword_comment_list,
                                    'KC':keyword_count_list,
                                    'KCC':keyword_commment_count_list
                                    })

    youtube_dataframe.to_csv('Crawled Data/{}/{}_youtube_dataframe'.format(today, today), index=False)