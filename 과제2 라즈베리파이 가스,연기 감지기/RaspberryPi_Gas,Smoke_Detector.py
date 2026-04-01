from gpiozero import Buzzer, DigitalInputDevice         # 'gpiozero' 라이브러리에서 'Buzzer',' DigitalInputDevice' 클래스를 가져옴
import time                                             # 'time' 라이브러리를 가져옴
                                                        # 'Buzzer' 클래스는 'OutputDevice'를 상속한 클래스임
bz = Buzzer(18)                                         # GPIO 18번 핀을 부저 제어 핀으로 초기화
gas = DigitalInputDevice(17)                            # GPIO 17번 핀을 MQ2 센서 입력 핀으로 초기화

try:
    while True:                                         # 무한 루프로 아래 동작반복
        if gas.value == 0:    # ← 0 = 가스 감지 (LOW)   # DO 핀이 0이면 가스 감지되었다고 판단하고
            print("가스 감지됨")                        # 터미널에 "가스 감지됨" 출력
            bz.on()                                     # 부저 작동
        else:                 # ← 1 = 정상 (HIGH)       # DO 핀이 1이면 정상 상태로 판단하고
            print("정상")                               # 터미널에 "정상" 출력
            bz.off()                                    # 부저 꺼짐

        time.sleep(0.2)                                 # 0.2초 간격으로 위의 내용 반복

except KeyboardInterrupt:                               # Ctrl+c로 정상 종료
    pass

bz.off()                                                # 프로그램 종료 할 때 부저를 OFF 처리
