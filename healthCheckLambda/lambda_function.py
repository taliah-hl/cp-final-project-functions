import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': True,
            'message': '(Team12) Health Check success!'
        })
    }
