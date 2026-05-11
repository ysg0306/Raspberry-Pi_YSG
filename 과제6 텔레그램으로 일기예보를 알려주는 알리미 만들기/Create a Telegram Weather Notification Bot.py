import urllib.request           # 웹 요청 라이브러리 / request 라이브러리와 목적동일
import json                     # JSON 데이터 처리 라이브러리
import datetime                 # 날짜/시간 라이브러리
import asyncio                  # 비동기 실행 라이브러리
from telegram import Bot        # 텔레그램 봇 객체

telegram_id = 'chat ID'         # 텔레그램 chat_id
my_token = 'bot token'          # BotFather에서 만든 봇으로 발급받은 토큰
api_key = 'API 키'              # OpenWeatherMap에서 발급받은 API 키 입력

bot = Bot(token=my_token)       # 토큰으로 봇 객체 생성

ALERT_HOURS = [7, 10, 13, 16, 19, 22]           # 7시부터 3시간 간격으로 알림                         # Hourly alerts every 3 hours
ALERT_TIMES = ["08:30", "15:20"]                # 추가적으로 지정한 시간                        # Custom time alerts (add your times here)

def getWeather():   # 날씨 정보를 받아와 문자열로 바꾸어 반환하는 함수
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Seoul&appid={api_key}&units=metric&lang=en&cnt=8"
                    #OpenWeatherMap API에서 받은 서울 24시간 예보 URL
    with urllib.request.urlopen(url) as r:      # API에 요청을 보냄
        data = json.loads(r.read())             # API로 부터 받은 응답을 JSON으로 변환

    text = ""                                                           # 문자열 초기화
    for i in range(8):                                                  # 8개 시간대 순회
        item = data['list'][i]                                          # i번째 날씨 데이터 가져오기
        hour = str((int(item['dt_txt'][11:13]) + 9) % 24).zfill(2)      # 시간 추출 후 KST 변환
        temp = item['main']['temp']                                     # 기온 추출
        humi = item['main']['humidity']                                 # 습도 추출
        desc = item['weather'][0]['description']                        # 날씨 설명 추출
        text += f"({hour}h {temp}C {humi}% {desc})\n"                   # 출력형식에 맞게 추출한 데이터 정리하여 문자열에 추가

    return text                                                         # 정리한 날씨 문자열 반환

async def main():                                                       # 비동기 메인함수
    try:    
        while True:                                                     # 무한 반복
            now = datetime.datetime.now()                               # 현재 시간 받기
            hm = now.strftime('%H:%M')                                  # 현재 시,분 추출  # Current time as HH:MM (e.g. "08:30")

            is_alert_hour = now.hour in ALERT_HOURS and now.minute == 0 and now.second == 0   # Check scheduled hour alert
            is_alert_time = hm in ALERT_TIMES and now.second == 0       # 정각인지 확인,  지정 시간 알림 조건 확인                     # Check custom time alert

            if is_alert_hour or is_alert_time:                          # 조건에 맞으면 실행
                msg = getWeather()                                      # msg에 날씨정보 저장
                print(msg)                                              # 터미널에 메세지 출력
                await bot.send_message(chat_id=telegram_id, text=msg)   # 텔레그램으로 메세지 전송

            await asyncio.sleep(1)                                      # 1초 대기 후 반복

    except KeyboardInterrupt:      # Ctrl+C 입력 시 정상 종료를 위한 명령어
        pass

asyncio.run(main())      # 비동기 메인 함수 실행
