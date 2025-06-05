import boto3
import json

IOT_ENDPOINT = "a2l2r8z087kz73-ats.iot.ap-southeast-2.amazonaws.com"
THING_NAME = "Final_pi_test"

iot_data = boto3.client("iot-data", endpoint_url=f"https://{IOT_ENDPOINT}")

def lambda_handler(event, context):
    # TODO implement
    response = iot_data.get_thing_shadow(thingName=THING_NAME)
    payload = json.loads(response['payload'].read())
    desired_state = "on"
    reported_state = payload.get("state", {}).get("reported", {})

    if reported_state.get("notification") == "on":
        desired_state = "off"

    # 更新 shadow 的 desired state
    iot_data = boto3.client("iot-data", region_name="ap-southeast-2")
    
    payload = {
        "state": {
            "desired": {
                "notification": desired_state
            }
        }
    }

    response = iot_data.update_thing_shadow(
        thingName=THING_NAME,
        payload=json.dumps(payload)
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': True,
            'message': '(Team12) Notification success'
        })
    }
