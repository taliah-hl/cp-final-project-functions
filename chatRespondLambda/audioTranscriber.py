import boto3
import botocore
import base64
import json
import time
from urllib.parse import urlparse
import io

class AudioTranscriber:
    def __init__(self, bucket_name, region='ap-southeast-2'):
        self.bucket_name = bucket_name
        self.region      = region
        self.s3          = boto3.client('s3')
        self.transcribe  = boto3.client('transcribe', region_name=region)

    def upload_audio(self, audio_base64, s3_key):
        """
        Upload audio data to S3
        
        Parameters:
        - audio_data: Binary audio data or local file path
        - s3_key: S3 object key where the audio will be stored
        """
        self.s3_key = s3_key
        audio_data = base64.b64decode(audio_base64)
        audio_stream = io.BytesIO(audio_data)
        self.s3.upload_fileobj(audio_stream, self.bucket_name, s3_key)
        print(f"Uploaded binary audio data to s3://{self.bucket_name}/{s3_key}")

    def start_transcription(self, job_name, media_format='m4a', language_code='zh-TW'):
        self.job_name = job_name
        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{self.bucket_name}/{self.s3_key}'},
            MediaFormat=media_format,
            LanguageCode=language_code,
            OutputBucketName=self.bucket_name  # ⬅️ 加這個！
        )

        print(f"Started transcription job: {job_name}")
    
    def safe_start_transcription(self, job_name, media_format='m4a', language_code='zh-TW'):
        try:
            self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            print(f"⚠️ Job '{job_name}' already exists, deleting it first...")
            self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] in ['NotFoundException', 'BadRequestException']:
                print(f"✅ No existing job named '{job_name}', ready to start.")
            else:
                raise e  # 其他錯誤才拋出
        # 開新 job
        self.start_transcription(job_name=job_name, media_format=media_format, language_code=language_code)

    def wait_for_completion(self, max_wait_seconds=300):
        """
        Wait for the transcription job to complete with a timeout
        
        Parameters:
        - max_wait_seconds: Maximum time to wait in seconds (default: 300s/5min)
        
        Returns:
        - Job status ('COMPLETED', 'FAILED', or 'TIMEOUT')
        """
        print("Waiting for transcription to complete...")
        start_time = time.time()
        
        while True:
            # Check if we've exceeded the maximum wait time
            if time.time() - start_time > max_wait_seconds:
                print(f"Transcription job timed out after {max_wait_seconds} seconds")
                return 'TIMEOUT'
                
            status = self.transcribe.get_transcription_job(TranscriptionJobName=self.job_name)
            state = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if state in ['COMPLETED', 'FAILED']:
                break
                
            # Sleep to avoid hitting API rate limits
            time.sleep(5)

        if state == 'COMPLETED':
            self.transcript_file_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
        print(f"Transcription job {state}")
        return state

    def get_transcribed_text(self):
        """
        Get the transcribed text from the completed job
        Uses in-memory processing instead of local files for Lambda compatibility
        """
        status = self.transcribe.get_transcription_job(TranscriptionJobName=self.job_name)
        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        print('Transcript file URI:', transcript_uri)

        parsed_url = urlparse(transcript_uri)
        path_parts = parsed_url.path.lstrip('/').split('/')
        bucket = path_parts[0]
        key = '/'.join(path_parts[1:])

        print(f"Parsed bucket: {bucket}, key: {key}")

        # Use in-memory processing instead of local files
        s3_response = self.s3.get_object(Bucket=bucket, Key=key)
        json_content = s3_response['Body'].read().decode('utf-8')
        result_json = json.loads(json_content)
        
        text = result_json['results']['transcripts'][0]['transcript']
        return text

    def delete_transcription_job(self):
        self.transcribe.delete_transcription_job(TranscriptionJobName=self.job_name)
        print(f"Deleted transcription job: {self.job_name}")

