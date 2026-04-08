from gpiozero import MotionSensor                                   # gpiozero 라이브러리에서 MotionSensor 클래스를 가져옴
import time                                                         # time.sleep사용을 위해 time 라이브러리를 가져옴
from picamera2 import Picamera2                                     # picamera2 라이브러리에서 Picamera2 클래스를 가져옴
import datetime                                                     # 날짜/시간 처리를 위한 datetime 라이브러리를 가져옴

pirPin = MotionSensor(16)                                           # GPIO 16번 핀을 PIR 모션 센서 입력 핀으로 초기화

picam2 = Picamera2()                                                # Picamera2 객체 생성
camera_config = picam2.create_preview_configuration()               # 카메라 미리보기 설정
picam2.configure(camera_config)                                     # 카메라 설정 적용
picam2.start()                                                      # 카메라 시작

try:                                                                
    while True:                                                     # 무한 루프로 아래 동작반복(센서로 감지시 촬영) 
        try:
            sensorValue = pirPin.value                              # PIR 센서의 현재 값을 읽어 변수에 저장
            if sensorValue == 1:                                    # 감지된 값이 1(움직임을 감지)인 경우 아래 코드들 실행
                now = datetime.datetime.now()                       # 현재 날짜, 시간을 가져옴 
                print(now)                                          # 감지시간을 터미널에 출력
                fileName = now.strftime('%Y-%m-%d %H:%M:%S')        # 파일이름에 활용할 촬영시간(년,달,일 시,분,초)을 flieName 변수에 저장
                picam2.capture_file(fileName + '.jpg')              # flieName + ".JPG"파일명으로 JPG 확장자 파일 생성
                time.sleep(0.5)                                     # 연속 촬영 방지를 위해서 0.5초간 대기
        except:                                                     # 루프 중 오류 발생 시 무시하고 진행
            pass

except KeyboardInterrupt:                                           # 키보드 인터럽트(Ctrl+C) 발생 시 루프 종료

    pass