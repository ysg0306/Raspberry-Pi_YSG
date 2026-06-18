import cv2                                              # OpenCV 라이브러리
import time                                             # 시간 제어를 위한 라이브러리
import asyncio                                          # 비동기 실행 라이브러리
from gpiozero import DigitalInputDevice, LED, Buzzer    # gpio 제어를 위한 'gpiozero' 라이브러리에서 'LED', 'Buzzer',' DigitalInputDevice' 클래스를 가져옴
from telegram import Bot                                # 텔레그램 봇을 제어하기 위한 봇 객체 생성
from telegram.ext import Application, CommandHandler    # 텔레그램에서 입력된 명령어를 처리하기 위해 사용

#GPIO 핀설정 
pir = DigitalInputDevice(18)    # GPIO 18번 핀을 PIR 인체감지 센서로 초기화
sound = DigitalInputDevice(24)  # GPIO 24번 핀을 소리 감지 센서로 초기화
led = LED(25)                   # GPIO 25번 핀을 LED로 초기화
buzzer = Buzzer(23)             # GPIO 23번 핀을 부저로 초기


system_enabled = True  # 시스템의 켜짐/꺼짐 관리

TELEGRAM_TOKEN = "텔레그램 토큰 입력"       #TELEGRAM_TOKEN 
USER_CHAT_ID = "유저 챗 아이디 입력"        #USER_CHAT_ID

# OpenCV 가중치 파일 로드 (안면 인식용)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 타이머 및 경보 플래그 변수 글로벌 정의 및 초기화
face_start_time = None          # 처음으로 얼굴 감지된 시간 기록
last_face_detected_time = None  # 마지막으로 얼굴 감지된 시간 기록 (비교하여 잠시 유예 시간을 주기 위함)
sound_start_time = None         # 처음으로 소리 감지된 시간 기록
last_sound_detected_time = None # 마지막으로 소리 감지된 시간 기록 (비교하여 잠시 유예 시간을 주기 위함)
no_activity_start_time = None   # 얼굴이나 소리 등 아무런 요소가 감지되지 않기 시작 시간 기록

face_alarm_triggered = False    # 얼굴 감지로 인한 경보가 이미 발생했는지 여부
sound_alarm_triggered = False   # 소리 감지로 인한 경보가 이미 발생했는지 여부


async def start_command(update, context): #텔레그램 내에서 /on으로 실행되는 비동기적 함수 (시스템 활성화)
    global system_enabled, face_start_time, last_face_detected_time, sound_start_time, last_sound_detected_time, face_alarm_triggered, sound_alarm_triggered, no_activity_start_time
    system_enabled = True #전역변수 불러오고 시스템활성화
    
    # 변수 초기화
    face_start_time = None
    last_face_detected_time = None
    sound_start_time = None
    last_sound_detected_time = None
    no_activity_start_time = None
    face_alarm_triggered = False
    sound_alarm_triggered = False
    print("방법시스템이 활성화 되었습니다.") #방범 시스템 활성화 메세지 텔레그램, 터미널에 출력
    await update.message.reply_text("🚨 [활성화] 지능형 방범 시스템이 활성화되었습니다. 감시를 시작합니다.")

async def stop_command(update, context): #텔레그램 내에서 /off로 실행되는 비동기적 함수 (시스템 비활성화)
    global system_enabled
    system_enabled = False  # 시스템 비활성화
    buzzer.off()            # LED,부저 비활성화
    led.off()
    print("방법시스템이 비활성화 되었습니다.") #방범 시스템 비활성화 메세지 텔레그램, 터미널에 출력
    await update.message.reply_text("🔒 [비활성화] 지능형 방범 시스템이 비활성화되었습니다. 안전 모드입니다.")

# 동시 만족 시 10초 동안 경보(부저 작동 + LED 깜빡임)를 발생시키는 비동기 함수
async def trigger_combined_alarm():
    print("🚨 [비상 경보] 부저 및 LED 10초간 경보 시작!")
    end_time = time.time() + 10.0 # 10초간 아래 코드 반복 
    while time.time() < end_time:
        if not system_enabled:   #off명령어 확인 위함
            break
        buzzer.on() # 부저 발생
        led.on()    # 3초 간격으로 LED 발광
        await asyncio.sleep(0.3)
        led.off()
        await asyncio.sleep(0.3)
    buzzer.off() #끝나면 비활성화
    led.off()

# 메인알고리즘 비동기 함수
async def monitor_system(app_bot):
    global system_enabled, face_start_time, last_face_detected_time, sound_start_time, last_sound_detected_time
    global face_alarm_triggered, sound_alarm_triggered, no_activity_start_time
    # 전역 변수 선언 및 카메라 상태 초기화
    camera = None
    camera_active = False  
    
    print("시스템 가동 시작. PIR 센서 감지를 대기합니다.")# 시작 알림
    
    try:
        while True:# 시스템을 계속 돌리기 위한 루프문, 0.05초 간격으로 처리
            await asyncio.sleep(0.05)
            
            if not system_enabled: #시스템 비활성화시 카메라 안전하게 종료 1초 간격으로 확인
                if camera_active and camera is not None:
                    camera.release()
                    cv2.destroyAllWindows()
                    camera_active = False
                await asyncio.sleep(1)
                continue
            
            pir_state = pir.value #PIR 센서 감지값
            
            # PIR 센서 감지 시 카메라 켜기
            if pir_state == 1 and not camera_active:
                print("🏃 움직임 포착! 카메라 전원을 켜고 영상 분석을 개시합니다.")
                
                # 변수 초기화
                face_start_time = None
                last_face_detected_time = None
                sound_start_time = None
                last_sound_detected_time = None
                no_activity_start_time = None
                face_alarm_triggered = False
                sound_alarm_triggered = False
                
                camera = cv2.VideoCapture(0) #웹캠 받아서 영상크기 설정하고 작동상태 활성화
                camera.set(3, 640)
                camera.set(4, 480)
                camera_active = True
            
            # 카메라 분석
            if camera_active:
                ret, frame = camera.read()
                if not ret:
                    continue
                
                current_time = time.time()
                
                # 안면 인식 연산
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=4)
                face_detected = len(faces) > 0
                
                # 얼굴 인식
                if face_detected:
                    last_face_detected_time = current_time  #유예시간을 위해 측정
                    if face_start_time is None:
                        face_start_time = current_time
                        print("👤 얼굴 감지 및 카운트다운 시작...")
                
                # 마지막 감지 후 2.5초가 지나지 않았다면 타이머 유지
                if face_start_time is not None:
                    if (current_time - last_face_detected_time) > 2.5:
                        # 얼굴이 시야에서 완전히 사라진 지 2.5초가 지났다면 리셋
                        face_start_time = None
                        face_alarm_triggered = False
                        print("🔄 얼굴이 감지되지 않아 타이머가 리셋되었습니다.")
                    elif (current_time - face_start_time) >= 10.0 and not face_alarm_triggered:
                        # 최초 감지 시점으로부터 누적 10초를 넘기면 활성화
                        face_alarm_triggered = True
                        print("✉️ [침입자 감지] 얼굴 10초 지속 감지! 텔레그램 전송 시작")
                        try:
                            photo_path = "intruder_face.jpg" # 파일 이름 설정
                            cv2.imwrite(photo_path, frame) #이미지 저장
                            await app_bot.send_message(chat_id=USER_CHAT_ID, text="⚠️ [침입자 감지] 외부인이 지속적으로 포착되었습니다!") #메세지 보내기
                            with open(photo_path, 'rb') as f: #캡쳐한 사진을 텔레그램 서버에 업로드
                                await app_bot.send_photo(chat_id=USER_CHAT_ID, photo=f)
                        except Exception as e:
                            print(f"텔레그램 전송 에러: {e}")
                
                # 소음 인식
                if sound.value == 1:
                    last_sound_detected_time = current_time #유예시간을 위해 측정
                    if sound_start_time is None:
                        sound_start_time = current_time
                        print("🔊 소음 카운트다운 시작...")
                
                if sound_start_time is not None:
                    if (current_time - last_sound_detected_time) > 2.0: # 2초의 유예시간
                        sound_start_time = None
                        sound_alarm_triggered = False
                        print("🔄 소음이 중단되어 타이머가 리셋되었습니다.") #소음이 감지된지 2초가 지나면 리셋
                    elif (current_time - sound_start_time) >= 10.0 and not sound_alarm_triggered: 
                        sound_alarm_triggered = True # 최초 감지 시점으로부터 누적 10초를 넘기면 활성화
                        print("✉️ [소음 감지] 지속적 소음 감지! 텔레그램 전송 시작")
                        try: #메세지 보내기
                            await app_bot.send_message(chat_id=USER_CHAT_ID, text="💥 [소음 감지] 지속적인 큰 충격 소음이 검출되었습니다!")
                        except Exception as e:
                            print(f"텔레그램 전송 에러: {e}")
                
                # [두 조건 동시 만족 처리] 동시에 만족하면 알람 트리거 발생 후 경고 발생
                if face_start_time is not None and sound_start_time is not None:
                    if (current_time - face_start_time >= 10.0) and (current_time - sound_start_time >= 10.0):
                        asyncio.create_task(trigger_combined_alarm())
                        face_start_time = None
                        sound_start_time = None
                        await app_bot.send_message(chat_id=USER_CHAT_ID, text="!!!!!!! 비상 [지속적인 소음과 외부인 감지] 비상 !!!!!!!")
                        
                # 절전 모드 전환
                # 10초간 얼굴 감지 안되고, PIR도 감지가 없을 때 절전모드 활성화 (카메라 비활성화)
                if (face_start_time is None) and (pir_state == 0):
                    if no_activity_start_time is None:
                        no_activity_start_time = current_time
                    elif current_time - no_activity_start_time >= 10.0:
                        print("💤 10초간 무반응. 절전모드를 활성화 합니다.")
                        camera.release()
                        cv2.destroyAllWindows()
                        camera_active = False
                        no_activity_start_time = None
                else:
                    no_activity_start_time = None
                
                if camera_active: #카메라 켜져있을때 얼굴 범위에 사각형 그리기
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.imshow('AIoT Guardian System', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

    except KeyboardInterrupt: #ctrl+c로 안전히 종료,카메라 비활성화
        print("\n프로그램을 종료합니다.")
    finally:
        if camera is not None:
            camera.release()
        cv2.destroyAllWindows()

# 메인함수
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build() # 텔레그램 통신을 위함
    application.add_handler(CommandHandler("on", start_command)) #/on입력시 start_command함수 실행하도록 매핑
    application.add_handler(CommandHandler("off", stop_command)) #/off입력시 stop_command함수 실행하도록 매핑
    #텔레그램 봇 백그라운드 수신작
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await monitor_system(application.bot) #방범 시스템 알고리즘 루프 실행
    #안전한 자원해제
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

if __name__ == "__main__": #메인함수가 비동기이기에 이런방식 활용해야함
    asyncio.run(main())
