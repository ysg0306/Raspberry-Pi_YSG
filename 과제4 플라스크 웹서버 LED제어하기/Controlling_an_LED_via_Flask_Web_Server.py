from flask import Flask, request, render_template   # Flask 웹서버를 만들기 위한 flask 라이브러리에서 Flask, request, render_template 클래스를 가져옴
from gpiozero import LED                            # gpiozero 라이브러리에서 'LED' 클래스를 가져옴 

app = Flask(__name__)                               # Flask 앱 생성

red_led = LED(21)                                   # 21번 핀에 연결된 LED 설정

@app.route('/')                                     # 주소에 (/) 접속 시 실행
def home():                                         # 기본화면에서
   return render_template("index.html")             # index.html 파일을 브라우저에 띄움

@app.route('/data', methods = ['POST'])             # /data 주소로  POST 요청 왔을 때 실행
def data():
    data = request.form['led']                      # HTML에서 'led'값 가져오기
    
    if(data == 'on'):                               # led값이 'on'이면 
        red_led.on()                                # LED 켜기

    elif(data == 'off'):                            # led값이 'off'면
        red_led.off()                               # LED 끄기

    return home()                                   # 메인페이지로 돌아오기

if __name__ == '__main__':
   app.run(host = '0.0.0.0', port = '80')           # 모든 IP(0.0.0.0)에서 80번 포트(HTTP 기본포트)로 서버 실행