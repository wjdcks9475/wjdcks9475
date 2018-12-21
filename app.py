# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
from operator import itemgetter

app = Flask(__name__)

slack_token = "xoxp-507548277458-507443611683-507408949892-8bcc06c4f3e07f82a2901a835912035f"
slack_client_id = "507548277458.508978605670"
slack_client_secret = "6a17b8b4f2186294a740cae133b5cf4d"
slack_verification = "HJvhhjWOJn1WhyPgYsWZlcWf"
sc = SlackClient(slack_token)
#Top10 함수
def _crawl_cotents_top(text):
    url_str = ""
    if "뮤지컬" in text:
        url_str = "01011"
    elif "콘서트" in text:
        url_str = "01003"
    elif "연극" in text:
        url_str = "01009"
    else:
        print("공연 Top10")
    print(text)
    url = "http://ticket.interpark.com/contents/Ranking/RankList?pKind=" + url_str + "&pCate=&pType=D&pDate=20181220"
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    titles = []
    keywords = []
    result = []
    for i, title in enumerate(soup.find_all("div", class_="prdInfo")):
        if not title.get_text() in titles:
            # 10개만
            if len(titles) >= 10:
                break
            titles.append(title.get_text().strip().replace('\n', '').replace('\t', '').replace('\r', ''))
        # print(titles)
    result.append(text[15:]+" Top 10")
    for text in titles:
        # while "  " in text:
        text = text.split("                                    ")
        keywords.append(text)
    print(keywords)
    for a,i in enumerate(keywords):
        temp = str(a+1)+" 위 :"+i[0] + "  장소 : " + i[1]
        result.append(temp)
    return result
#유사도 찾기 함수
def _crawl_place_search(text):
    print(type(text))
    url = "http://ticket.interpark.com/contents/Ranking/RankList?pKind=P&pCate=&pType=D&pDate=20181220"
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    titles = []
    keywords = []
    match_data = []
    temp0 =[]
    calc_data = []
    result = []
    for i, title in enumerate(soup.find_all("div", class_="prdInfo")):
        if not title.get_text() in titles:
            # 50개만
            if len(titles) >= 50:
                break
            titles.append(title.get_text().strip().replace('\n', '').replace('\t', '').replace('\r', ''))

        # print(titles)

    for i, temp in enumerate(titles):
        # while "  " in text:
        temp = temp.split("                                    ")
        temp.append(str(i+1))
        keywords.append(temp)
    print(keywords)
    percent=[]
    dict={}
    max = 0
    text = text[16:]

    for title_place in keywords:
        if str(text) in title_place[1]:
            temp2 =len(text)/len(title_place[1])
            dict[title_place[2]] = float(temp2)
    temp3 =list(dict.items())
    dict = sorted(temp3, key=itemgetter(1), reverse=True)
    for i in range(0,len(dict)):
        temp0.append(str(i+1)+ "위 : "+ keywords[int(dict[i][0])-1][0] + "  장소 : "+keywords[int(dict[i][0])-1][1] + "  검색 유사도: "+str(int(dict[i][1]*100))+"%")
    #print(dict)
    #print(calc_data)

    return temp0
# 시간대 찾기 함수
def _crawl_time(text) :
    url = "http://ticket.interpark.com/contents/Ranking/RankList?pKind=P&pCate=&pType=D&pDate=20181220"
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")
    titles = []
    for i, title in enumerate(soup.find_all("td", class_="prdDuration")):
        if not title.get_text() in titles:
            # 10위까지만 크롤링하겠습니다.
            titles.append(
                title.get_text().strip().replace('\n', '').replace('\r', '').replace('\t', '').replace('.', ''))


    dates = []
    for title in titles:
        if "~" in str(title):
            title = title.split('~')
            dates.append(title)
        else:
            dates.append([title, title])
    for date in dates:
        date[0]=date[0][-8:]
        date[1]=date[1][-8:]
        for i in range(0, len(date)):
            date[i] = int(date[i])
    print(dates)
    index=[]
    temp=text[16:]
    for i in range(0,len(dates)):
        if dates[i][0]<=int(text[16:])<=dates[i][1]:
            index.append(str(i))
    titles = []
    keywords = []
    result = []
    for i, title in enumerate(soup.find_all("div", class_="prdInfo")):
        if not title.get_text() in titles:
            # 10개만
            titles.append(title.get_text().strip().replace('\n', '').replace('\t', '').replace('\r', ''))
        # print(titles)

    for text in titles:
        # while "  " in text:
        text = text.split("                                    ")
        keywords.append(text)
    result.append("선택한 날짜 : "+str(temp)+" 에 관람 가능한 공연 목록")
    for i in range(0,len(index)):
        result.append("공연명 : "+keywords[i][0]+"  장소 : "+ keywords[i][1])
    return result

# Main 함수
def _crawl_naver_keywords(text):

    # 여기에 함수를 구현해봅시다.
    result=[]
    if "순위" in text:
        result = _crawl_cotents_top(text)
    elif "장소" in text:
        result = _crawl_place_search(text)
    elif "날짜" in text:
        result = _crawl_time(text)
    else :
        result.append("다시 입력해주세요 ")


    return u'\n'.join(result)

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
