from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import os
import time
import json
import pygame
from piModules.Recorder import Recorder
from piModules.Picam    import MyPicam
from AwsBot import AwsBot
from pathlib import Path

base_dir = os.path.dirname(os.path.abspath(__file__))
# 需要用新的換掉
THING_NAME = "ResPiForFinal"
ENDPOINT = "a2rwg7fxsn0b1i-ats.iot.us-east-1.amazonaws.com"


def handle_delta_callback(payload, response_status, token):
    #print("收到 Shadow delta 訊息：")
    print("[Delta Callback] payload:", payload)
    try:
        data = json.loads(payload)
        cue_state = data["state"].get("cue")
        notification_state = data["state"].get("notification")

        if notification_state:
            try:
                pygame.mixer.music.stop()
                # 回報狀態為 reported
                reported_payload = {
                    "state": {
                        "reported": {
                            "notification": notification_state
                        }
                    }
                }
                device_shadow.shadowUpdate(json.dumps(reported_payload), None, 5)
            except:
                pass
            pygame.mixer.music.load(str(can_dir / 'ActivitiesNotice.mp3'))
            pygame.mixer.music.play(start=4.0)
            
        if(cue_state == "Cue me"):
            rec.start()
            picam.capture(img_dir / 'img.jpg')
            # 回報狀態為 reported
            reported_payload = {
                "state": {
                    "reported": {
                        "cue": cue_state
                    }
                }
            }
            device_shadow.shadowUpdate(json.dumps(reported_payload), None, 5)
        elif(cue_state == "Cue ok"):
            msg               = ''
            
            rec.stop()
            
            try:
                pygame.mixer.music.stop()
                # 回報狀態為 reported
                reported_payload = {
                    "state": {
                        "reported": {
                            "cue": cue_state
                        }
                    }
                }
                device_shadow.shadowUpdate(json.dumps(reported_payload), None, 5)
            except:
                pass
            interlude = pygame.mixer.Sound(str(can_dir / 'Interlude.mp3'))
            # pygame.mixer.music.load(str(can_dir / 'Interlude.mp3'))
            interlude.set_volume(0.3)
            interlude.play(loops=-1)
            
            msg = bot.speech_to_text(rec_dir / 'record.wav')
            print(f"Speech content   : {msg}")
            
            
            res_text = bot.image_to_response(msg, str(img_dir / 'img.jpg'), str(wk_dir / 'chat_record.txt'))
            print(f"Response : {res_text}")
            # print(res_text)
            
            bot.text_to_speech(res_text, sph_dir / 'response.mp3')
            
            interlude.stop()
            pygame.mixer.music.load(str(sph_dir / 'response.mp3'))
            pygame.mixer.music.play()
            
            # # Wait until the sound finishes
            # while pygame.mixer.music.get_busy():
            #     pygame.time.Clock().tick(10)
        
    except Exception as e:
        print("[Delta Handler] 發生錯誤:", e)

if __name__ == "__main__":
    # 建立工作目錄與元件
    wk_dir = Path(os.path.dirname(__file__))
    rec_dir = wk_dir / 'tmp/userRecording'
    sph_dir = wk_dir / 'tmp/responseSpeech'
    img_dir = wk_dir / 'tmp/userPhoto'
    can_dir = wk_dir / 'resources/can_audio'
    for d in [rec_dir, sph_dir, img_dir, can_dir]: d.mkdir(parents=True, exist_ok=True)

    rec = Recorder(str(rec_dir))
    bot = AwsBot()
    picam = MyPicam()
    picam.start()
    pygame.mixer.init()

    # 建立 Device Shadow 連線
    shadow_client = AWSIoTMQTTShadowClient("DeviceController")
    shadow_client.configureEndpoint(ENDPOINT, 8883)
    shadow_client.configureCredentials("root-CA.crt", "device.key", "device.crt")
    shadow_client.connect()

    device_shadow = shadow_client.createShadowHandlerWithName(THING_NAME, True)

    # 訂閱 delta
    device_shadow.shadowRegisterDeltaCallback(handle_delta_callback)

    print("等待指令中...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("中止程式")
        picam.close()

