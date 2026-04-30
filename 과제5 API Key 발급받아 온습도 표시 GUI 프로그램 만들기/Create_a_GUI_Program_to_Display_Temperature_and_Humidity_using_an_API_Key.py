import urllib.request, json, tkinter, tkinter.font  
# 웹에 데이터 요청하는 urllib.request 라이브러리
# JSON 데이터 처리하는 json 라이브러리
# GUI 창 만드는 tkinter 라이브러리
# tkinter 폰트 설정하는 tkinter.font 라이브러리를 받아옴
API_KEY = "비공개(API키 적는칸)"        #openweathermap사이트에서 로그인하고 얻은 api키를 입력
 
def tick1Min(): #1분마다 반복하는 함수  (날씨데이터를 받아와 온도, 습도 추출함)
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric" # 서울 날씨 요청하기 위한 URL+개인 API키
    with urllib.request.urlopen(url) as r:      # API키를 포함한 URL을 통해 웹 사이트에서 정보를 요청
        data = json.loads(r.read())             # 받은 응답을 JSON 형태로 변환
    temp = data["main"]["temp"]                 # 데이터에서 온도 받아옴
    humi = data["main"]["humidity"]             # 데이터에서 습도 받아옴
    label.config(text=f"{temp:.1f}C   {humi}%") # 라벨 텍스트 업데이트
    window.after(60000, tick1Min)               # 1분 마다 함수 재실행
 
window = tkinter.Tk()                               # 창 생성
window.title("TEMP HUMI DISPLAY")                   # 창 제목 TEMP HUMI DISPLAY로 설정
window.geometry("400x100")                          # 창 크기 설정 (가로X세로)
window.resizable(False, False)                      # 창크기 조절 불가하도록 설정
font = tkinter.font.Font(size=30)                   # 폰트 크기 30 설정
label = tkinter.Label(window, text="", font=font)   # 텍스트 라벨 생성
label.pack()                                        # 라벨을 창에 배치
tick1Min()                                          # 1분마다 실행되도록 함수 호출
window.mainloop()                                   # 창 유지
