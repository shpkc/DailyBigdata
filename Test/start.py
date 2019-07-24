from DaumCrawler import Daum
from InstagramCralwer import Instagram
from TwitterCrawler import Twitter
from YoutubeCrawler import Youtube
from SentimentAnalysis import LSTM
from MakingText import Text
import time
import schedule

if __name__ == "__main__":
    
    start_time = time.time()

    Daum()
    Instagram()
    Twitter()
    Youtube()
    LSTM()
    Text()

    print("총 걸린시간 : {}분".format(round((time.time() - start_time)/60, 1)))

# 매일 아침 6시5분에 크롤링 설정
'''
def everything():

    start_time = time.time()

    Daum()
    Instagram()
    Twitter()
    Youtube()
    LSTM()
    Text()

    print("총 걸린시간 : {}분".format(round((time.time() - start_time)/60, 1)))
    
schedule.every().day.at("06:05").do(everything)

while True:
    schedule.run_pending()
    time.sleep(1)
'''