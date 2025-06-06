import json
import boto3
# start
def lambda_handler(event, context):
    try:
    # TODO implement
    # 更新 shadow 的 desired state
        iot_data = boto3.client("iot-data", region_name="ap-southeast-2")
    
        payload = {
            "state": {
                "desired": {
                    "cue": "start"
                }
            }
        }

        response = iot_data.update_thing_shadow(
            thingName="Final_pi_test",
            payload=json.dumps(payload)
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': "cue start is updated",
                'cueState': 'cued'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': "error in cue me occur",
                'error': str(e)
            })
        }
