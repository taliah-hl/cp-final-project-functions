import json
import boto3
import base64
import time

# 偶像人設 prompt
PERSONALITY_PROMPT = """
你是一個五人組成的偶像男團FEnix的現役成員-夏浦陽,27歲男生,團隊內的舞蹈擔當。
性格溫暖陽光,很真性情,像個小太陽,也喜歡與朋友開玩笑。
你們團隊(FEnix)的粉絲名叫救火隊,而你個人的粉絲則叫做洋咩咩,
粉絲們都很熟悉並喜歡你,你們很常進行日常的互動。
請沉浸式帶入角色跟粉絲互動,並模仿以下對話風格：
"""

REMINDER = """
切記,請模仿口氣但內容須對應粉絲的提問,避免死板複製。回覆盡量三句話以下,偶爾可多一點。
不要直接提到範例,要當作自己的即興對話。
"""

# 上傳圖片到 S3
def upload_image_to_s3(image_base64_str, bucket_name, key):
    s3 = boto3.client('s3')
    try:
        image_bytes = base64.b64decode(image_base64_str)
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=image_bytes,
            ContentType="image/jpeg"
        )
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
        print(f"[✓] Image uploaded to S3: {s3_url}")
        return s3_url
    except Exception as e:
        print(f"[✗] Failed to upload image to S3: {e}")
        return None

# 主流程：生成回覆
def get_chat_respond(message, image_base64, chat_history=""):
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name="ap-southeast-2"
    )

    # 組 prompt
    system_prompt = PERSONALITY_PROMPT + "\n請以偶像身分對這圖片作出回應。\n"
    system_prompt += "注意！請尊重個資對人物進行描述，不使用 emoji。\n"
    system_prompt += REMINDER

    user_prompt = ""
    if chat_history:
        user_prompt += "以下是之前的聊天記錄：\n" + chat_history + "\n"
    user_prompt += "粉絲訊息：" + message

    # 上傳圖片到 S3（非必要，可省略）
    image_s3_url = upload_image_to_s3(
        image_base64_str=image_base64,
        bucket_name="team12-chatbot",
        key=f"chat-images/image.jpg"
    )

    # 組模型請求
    request_body = {
        "schemaVersion": "messages-v1",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": user_prompt},
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {
                                "bytes": image_base64
                            }
                        }
                    }
                ]
            }
        ],
        "system": [
            {"text": system_prompt}
        ],
        "inferenceConfig": {
            "maxTokens": 500,
            "topP": 0.9,
            "topK": 20,
            "temperature": 0.7
        }
    }

    # 呼叫 Bedrock 模型
    response = bedrock_runtime.invoke_model(
        modelId="arn:aws:bedrock:ap-southeast-2:701030859948:inference-profile/apac.amazon.nova-lite-v1:0",
        body=json.dumps(request_body)
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        response_body = response["body"].read().decode("utf-8")
        response_json = json.loads(response_body)
        respond_message = response_json['output']['message']['content'][0]['text']
        print(f"🗣️ 回覆訊息: {respond_message}")
        return {
            "message": respond_message,
            "image_url": image_s3_url
        }
    else:
        print("❌ 模型呼叫失敗")
        return 'error'
