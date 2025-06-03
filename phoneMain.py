from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from android.permissions import request_permissions, Permission
from jnius import autoclass
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
import threading

class BluetoothApp(App):
    def build(self):
        self.bt_socket = None
        self.recording = False # recording
        self.notification_state = False

        layout = BoxLayout(orientation='vertical')
        
        # Cue Me Button
        self.cue_me_btn = Button(text="Cue Me!", disabled=True)
        self.cue_me_btn.bind(on_press=self.send_cue_me)
        layout.add_widget(self.cue_me_btn)
        
        # Notification Button
        self.ntf_btn = Button(text="Notification!", disabled=True)
        self.ntf_btn.bind(on_press=self.send_notification)
        layout.add_widget(self.ntf_btn)
        

        return layout
    

    def update_shadow_state(self, state_name, value):
        shadow_client = AWSIoTMQTTShadowClient("mobile-controller")
        shadow_client.configureEndpoint("your-iot-endpoint.amazonaws.com", 8883)
        shadow_client.configureCredentials("root-ca.pem", "private.key", "certificate.pem.crt")
        shadow_client.connect()
        
        device_shadow = shadow_client.createShadowHandlerWithName("your-thing-name", True)
        
        payload = {
            "state": {
                "desired": {
                    state_name: value
                }
            }
        }
        device_shadow.shadowUpdate(json.dumps(payload), None, 5)

            
    def send_cue_me(self, instance):
        if not self.recording:
            self.update_shadow_state("cue", "Cue me")
            self.cue_me_btn.text = "Cue ok."
            self.recording = True
        else:
            self.update_shadow_state("cue", "Cue ok")
            self.cue_me_btn.text = "Cue me."
            self.recording = False

        
    def send_interact(self, instance):
        if(self.recording == False):
            threading.Thread(target=self._start_recording).start()
        else:
            threading.Thread(target=self._end_recording).start()
            
    def send_notification(self, instance):
        if self.notification_state :
            self.notification_state = False
        else :
            self.notification_state = True
            
        self.update_shadow_state("notification", str(self.notification_state))
        
    def take_a_picture(self, instance):
        self._take_a_picture()
        
    def invoke_response(self, instance):
        self._invoke_response()
    
    
    def send_wifi(self, instance):
        pass
    
        
    def _start_recording(self):
        self.__send_to_device__("Start recording.")
        
        # Update state
        self.recording = True
        
        # Update UI
        # self.interact_btn.text = "Stop recording"
        self.cue_me_btn.text = "Cue ok!"
        
    def _end_recording(self):
        self.__send_to_device__("Stop recording.")
        
        # Update state
        self.recording = False
        
        # Update UI
        # self.interact_btn.text = "Start recording"
        self.cue_me_btn.text = "Cue Me!"
        
        
    def _take_a_picture(self):
        self.__send_to_device__("Take a picture.")
        
    def _invoke_response(self):
        self.__send_to_device__("Invoke response.")
        
    # def _send_data_to_pi(self):
    #     try:
    #         # Android Bluetooth classes
    #         BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    #         BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    #         UUID = autoclass('java.util.UUID')

    #         adapter = BluetoothAdapter.getDefaultAdapter()

    #         # Replace with your Pi's Bluetooth MAC address
    #         address = "DC:A6:32:8D:9B:A6"

    #         device = adapter.getRemoteDevice(address)

    #         # ⚠️ Here's the key change: Use insecure connection on port 1 (no SDP)
    #         socket = device.createRfcommSocket(1)  # ← Android hidden API, may fail

    #         # Cancel discovery if needed
    #         if adapter.isDiscovering():
    #             adapter.cancelDiscovery()

    #         socket.connect()

    #         # output = socket.getOutputStream()
    #         # message = "Hello Pi!"
    #         # output.write(bytes(message, "UTF-8"))
    #         # output.flush()
            
    #         # ---------- SEND --------------------------------------------------
    #         out_stream = socket.getOutputStream()
    #         msg        = b"Hello Pi!\n"
    #         out_stream.write(jarray('b', msg))
    #         out_stream.flush()
    #         print("> sent:", msg.decode().strip())

    #         # ---------- RECEIVE (blocking) ------------------------------------
    #         in_stream  = socket.getInputStream()
    #         buf        = jarray('b', 256)        # Java byte[] buffer
    #         received   = bytearray()

    #         while True:
    #             n = in_stream.read(buf)          # returns -1 on EOF
    #             if n == -1:
    #                 raise IOError("Pi closed the connection")

    #             received.extend(buf[:n])

    #             # stop when we see a newline
    #             if received.endswith(b"\n"):
    #                 break
                
    #         answer = received.decode("utf-8", "replace").strip()
    #         print("< recv:", answer)

    #         # socket.close()
    #         print("Message sent!")

    #     except Exception as e:
    #         print(f"[Bluetooth Error] {e}")

BluetoothApp().run()
