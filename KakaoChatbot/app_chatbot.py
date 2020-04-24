from flask import Flask, request, jsonify
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import urllib

ERROR_MESSAGE = 'Network Connecting Error'

app = Flask(__name__)

@app.route('/weather', methods=['POST'])
def weather():

    req = request.get_json()

    # location = req["action"]["detailParams"]["sys_location"]["value"]
    # print(location)
    # enc_loc = urllib.parse.quote(location + '+ 날씨')
    # el = str(enc_loc)
    # url = 'https://search.naver.com/search.naver'
    # url = url + '?sm=top_hty&fbm=1&ie=utf8&query='
    # url = url + el

    # req = Request(url)
    # page = urlopen(req)
    # html = page.read()
    # soup = BeautifulSoup(html, 'html.parser')
    # r1 = soup.find('li', class_='on now merge1')
    # r2 = r1.find('dd', class_='weather_item _dotWrapper')
    # r3 = r2.find('span').text

    # rain_pct = int(r3)

    # if len(location) <= 0:
    #     answer = ERROR_MESSAGE
    # elif rain_pct < 30:
    #     answer = location + "의 강수 확률은 " + r3 + "%입니다 맑은 하루 되세요^_^"
    # else:
    #     answer = location + "의 강수 확률은 " + r3 + "%입니다 우산 챙겨가세요!!"
    
    answer = '날씨 정보 제공 서비스'
    
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }

    return jsonify(res)

@app.route('/movies', methods=['POST'])
def movies():
    req = request.get_json()
    # print(req)
    
    # 1. 작성 예시에서의 버튼으로 진입인지 메시지 입력 전송으로 진입인지 확인
    #    버튼은 예매 순위와 개봉 영화 정보만 제공함
    # 2. 
    path = req['intent']['extra']['reason']['message'] 
    if path == 'DIRECT_ID':
        if '개봉' in req['userRequest']['utterance']:
            answer = '입력 예시 창 버튼 입력_개봉예정영화'
        else:
            answer = '입력 예시 창 버튼 입력_예매율 순위'
        
    elif path == 'OK':
        answer = '사용자 전송 입력'
        
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }

    return jsonify(res)

# 메인 함수
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug = True, threaded=True)
