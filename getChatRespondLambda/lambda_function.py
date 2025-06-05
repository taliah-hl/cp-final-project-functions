import json
import os
import time
from audioTranscriber import AudioTranscriber
from chatBot import *
import boto3



def lambda_handler(event, context):
    """
    Lambda function that processes an image and gets a response from nove via Bedrock
    
    Expected event format:
    {
        "audio": "User audio",
        "image_base64": "Base64 encoded image data",
        "chat_history": "Optional chat history"
    }
    """
    

    try:
        lambda_client = boto3.client('lambda')
        # If event comes from API Gateway, extract and parse the body
        if "body" in event:
            # If body is already a dict, use it; otherwise, parse JSON string
            if isinstance(event["body"], dict):
                body = event["body"]
            else:
                body = json.loads(event["body"])
        else:
            body = event

        # Extract data from event
        audio_base64 = body.get('audio', '')
        image_base64 = body.get('image_base64', '')
        chat_history = body.get('chat_history', '')

        # if audio_base64 is not str or image_base64 is not str:
        if not isinstance(audio_base64, str) or not isinstance(image_base64, str) or not audio_base64 or not image_base64:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': f'Invalid input data format, image_base64: {image_base64}, audio_base64: {audio_base64}',
                    'error': 'audio_base64 and image_base64 must be strings'
                })
            }
        try:
            user_message = speech_to_text(audio_base64)
            print(f"user message: {user_message}")
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'Audio transcription failed',
                    'error': str(e)
                })
            }

        if user_message == "error":
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'Audio transcription failed',
                    'error': "unknown"
                })
            }
        
        try:
        
            respond_message = get_chat_respond(user_message, image_base64, chat_history)
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'Chat bot failed',
                    'error': str(e)
                })
            }

        if respond_message == 'error':
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'Chat bot failed',
                    'error': "unknown"
                })
            }
        
        # call TTS lamdba
        try:
            tts_response = lambda_client.invoke(
                FunctionName='Team12-TextToSpeech',  # 替換成你的 TTS Lambda 名稱
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    "text": respond_message,
                    "voice": "Zhiyu"  # 可選擇其他 Polly 支援的 VoiceId
                }).encode("utf-8")
            )

            tts_payload = json.loads(tts_response["Payload"].read())
            audio_url = json.loads(tts_payload["body"]).get("audio_url", "error")

            if audio_url == "error":
                raise Exception("TTS lambda failed to return audio_url")

        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": "TTS Lambda 呼叫失敗",
                    "error": str(e)
                })
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": respond_message,
                "audio_url": audio_url
            })
        }



    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': "error occur in lambda handler",
                'error': str(e)
            })
        }
        


def speech_to_text(audio_base64):
    # Initialize the transcriber
    transcriber = AudioTranscriber(bucket_name='team12-chatbot')

    # Upload the audio data to S3
    s3_key = 'conversation_audio/input_audio.wav'  # Adjust the path as needed
    transcriber.upload_audio(audio_base64, s3_key)

    # Start transcription job
    job_name = f"audio_to_text_job_{int(time.time())}"
    transcriber.safe_start_transcription(job_name=job_name, media_format='wav', language_code='zh-TW')


    if transcriber.wait_for_completion() == 'COMPLETED':
        text = transcriber.get_transcribed_text()
        return text
    else:
        raise Exception("Transcription failed")