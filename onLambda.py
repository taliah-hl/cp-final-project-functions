# 這是在lambda上的
  import json
  import boto3

  def lambda_handler(event, context):
      print("Received event:", event)
      
      # 解析前端送來的內容
      body = json.loads(event["body"])
      command = body.get("command", "")
      state = body.get("state", "")
  
      # 更新 shadow 的 desired state
      iot_data = boto3.client("iot-data", region_name="ap-northeast-1")
      
      payload = {
          "state": {
              "desired": {
                  command: state
              }
          }
      }
  
      response = iot_data.update_thing_shadow(
          thingName="YourDeviceThingName",
          payload=json.dumps(payload)
      )
  # 可以回傳給裝置，雖然不知道幹嘛
      return {
          "statusCode": 200,
          "body": json.dumps({"message": f"Command '{command}' sent!"})
      }
