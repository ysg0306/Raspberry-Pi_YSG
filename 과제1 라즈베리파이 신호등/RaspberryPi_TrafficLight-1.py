from gpiozero import LED            # 'gpiozero' 라이브러리에서 'LED' 클래스를 가져옴
from time import sleep              # 'time' 라이브러리에서 'sleep' 함수를 가져옴

carLedRed = 2                       # 다양한 LED 핀의 핀 번호를 변수로 정의함 (Lines 4~8)
carLedYellow = 3                    # carLedRed, carLedYellow, carLedRed, carLedGreen, humanLedRed, humanLedGreen 변수에 각각 핀 번호를 할당
carLedGreen = 4
humanLedRed = 20
humanLedGreen = 21

carLedRed = LED(2)                  # 각 LED를 LED 클래스의 객체로 초기화하며, 핀 번호를 사용하여 LED 객체를 생성 (Lines 10~14)
carLedYellow = LED(3)
carLedGreen = LED(4)
humanLedRed = LED(20)
humanLedGreen = LED(21)

try:                                # whlie 1: 로 무한루프 시작,아래 내용 반복 (Lines 16 ~ 35)        
    while 1:                        # 변수.value 값이 0이면 LED 꺼짐, 값이 1이면 LED켜짐
        carLedRed.value = 0         # Sleep 함수를 사용해 대기 시간을 설정 (Lines 23,29,35)
        carLedYellow.value = 0
        carLedGreen.value = 1
        humanLedRed.value = 1
        humanLedGreen.value = 0
        sleep(3.0)                  
        carLedRed.value = 0
        carLedYellow.value = 1
        carLedGreen.value = 0
        humanLedRed.value = 1
        humanLedGreen.value = 0
        sleep(1.0)
        carLedRed.value = 1
        carLedYellow.value = 0
        carLedGreen.value = 0
        humanLedRed.value = 0
        humanLedGreen.value = 1
        sleep(3.0)
    
except KeyboardInterrupt:           # 사용자가 Ctrl + C를 누를 때까지 코드를 실행하는 예외 처리 블록임
    pass                            # 사용자가 Ctrl + C를 누르면 루프가 중단되고 코드 실행이 종료됨

carLedRed.value = 0                 # 코드 실행이 종료되면 .value 값을 0으로 바꿔줌으로써 LED를 꺼줌 (Lines 40 ~ 44)
carLedYellow.value = 0
carLedGreen.value = 0
humanLedRed.value = 0
humanLedGreen.value = 0