from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import os
import time
import json
import requests
import base64
"""
import pygame
from piModules.Recorder import Recorder
from piModules.Picam    import MyPicam
from AwsBot import AwsBot
from pathlib import Path
"""
base_dir = os.path.dirname(os.path.abspath(__file__))
# 需要用新的換掉
THING_NAME = "Final_pi_test"
ENDPOINT = "a2l2r8z087kz73-ats.iot.ap-southeast-2.amazonaws.com"

def report_state(state_name, state):
    reported_payload = {
        "state": {
            "reported": {
                state_name: state
            }
        }
    }
    device_shadow.shadowUpdate(json.dumps(reported_payload), None, 5)
    print(f"{state_name}: {state} reported")

def handle_delta_callback(payload, response_status, token):
    #print("收到 Shadow delta 訊息：")
    print("[Delta Callback] payload:", payload)
    try:
        data = json.loads(payload)
        cue_state = data["state"].get("cue")
        notification_state = data["state"].get("notification")

        if notification_state:
            try:
                #pygame.mixer.music.stop()
                # 回報狀態為 reported
                report_state("notification", notification_state)
            except:
                pass
            #pygame.mixer.music.load(str(can_dir / 'ActivitiesNotice.mp3'))
            #pygame.mixer.music.play(start=4.0)
            
        if(cue_state == "Cue me"):
            #rec.start()
            #picam.capture(img_dir / 'img.jpg')
            # 回報狀態為 reported
            report_state("cue", cue_state)
            
        elif(cue_state == "Cue ok"):
            msg               = ''
            
            #rec.stop()
            
            try:
                #pygame.mixer.music.stop()
                # 回報狀態為 reported
                report_state("cue", cue_state)
            except:
                pass

            # === 檔案路徑（請換成你的音訊與圖片實際路徑） ===
            audio_path = "user_prompt1_how_are_you.wav"
            image_path = "test_image.jpg"

            # === 將檔案轉為 base64 ===
            with open(audio_path, "rb") as audio_file:
                audio_b64 = base64.b64encode(audio_file.read()).decode("utf-8")

            with open(image_path, "rb") as image_file:
                image_b64 = base64.b64encode(image_file.read()).decode("utf-8")

            # === API URL ===
            url = "https://cagrxdp7g5.execute-api.ap-southeast-2.amazonaws.com/get-chat-respond"

            # === Payload ===
            payload = {
                "audio": audio_b64,
                "image_base64": image_b64,
                "chat_history": "Hi, this is my previous message."
            }

            # === 發送 POST 請求 ===
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)

            # === 檢查回應 ===
            if response.status_code == 200:
                print("Success! Response:")
                print(response.json())
            else:
                print(f"Request failed: {response.status_code}")
                print(response.text)

            """
            interlude = pygame.mixer.Sound(str(can_dir / 'Interlude.mp3'))
            # pygame.mixer.music.load(str(can_dir / 'Interlude.mp3'))
            interlude.set_volume(0.3)
            interlude.play(loops=-1)
            
            
            interlude.stop()
            pygame.mixer.music.load(str(sph_dir / 'response.mp3'))
            pygame.mixer.music.play()
            """
            # # Wait until the sound finishes
            # while pygame.mixer.music.get_busy():
            #     pygame.time.Clock().tick(10)
            
    except Exception as e:
        print("[Delta Handler] 發生錯誤:", e)

if __name__ == "__main__":
    # 建立工作目錄與元件
    """
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
    """
    cert_files = {
        "root_ca": os.path.join(base_dir, "root-CA.crt"),
        "private_key": os.path.join(base_dir, "Final_pi_test.private.key"),
        "cert": os.path.join(base_dir, "Final_pi_test.cert.pem")
    }
    # 建立 Device Shadow 連線
    shadow_client = AWSIoTMQTTShadowClient("DeviceController")
    shadow_client.configureEndpoint(ENDPOINT, 8883)
    shadow_client.configureCredentials(
        cert_files["root_ca"],
        cert_files["private_key"],
        cert_files["cert"]
    )
    shadow_client.connect()

    device_shadow = shadow_client.createShadowHandlerWithName(THING_NAME, True)

    # 訂閱 delta
    device_shadow.shadowRegisterDeltaCallback(handle_delta_callback)
    report_state("rpi", "connected")

    print("等待指令中...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("中止程式")
        report_state("rpi", "disconnected")
        #picam.close()

