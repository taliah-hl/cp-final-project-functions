import json
import os
import time
from audioTranscriber import AudioTranscriber
from chatBot import *

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
        # Extract data from event
        audio_base64 = event.get('audio', '')
        image_base64 = event.get('image_base64', '')
        chat_history = event.get('chat_history', '')
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
        
        # to do: call speech to text lamdba
        # try:
        #     pass
        # except Exception as e:
        #     return {
        #         'statusCode': 400,
        #         'body': json.dumps({
        #             'success': False,
        #             'message': 'Speech to text failed',
        #             'error': str(e)
        #         })
        #     }
        respond_audio = "dummy audio"   # simulate dummy audio

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': respond_message,
                'audio': respond_audio
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