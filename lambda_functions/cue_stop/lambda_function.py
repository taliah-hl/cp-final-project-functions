import boto3
import json

THING_NAME = "Final_pi_test"

def lambda_handler(event, context):
    try: 
        # TODO implement

        # 更新 shadow 的 desired state
        iot_data = boto3.client("iot-data", region_name="ap-southeast-2")
        
        payload = {
            "state": {
                "desired": {
                    "cue": "stop"
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
                'message': 'cue stop is updated',
                'cueState': 'idle'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': "error occur in stop cue",
                'error': str(e)
            })
        }
    
