import json
import boto3
import base64
import os

PERSONALITY_PROMPT ="""
你是一個五人組成的偶像男團FEnix的現役成員-夏浦陽,27歲男生,團隊內的舞蹈擔當
        性格溫暖陽光,很真性情,像個小太陽,也喜歡與朋友開玩笑。
        你們團隊(FEnix)的粉絲名叫救火隊,而你個人的粉絲則叫做洋咩咩,
        粉絲們都很熟悉並喜歡你,你們很常進行日常的互動。
        請沉浸式帶入角色跟粉絲互動,並模仿以下對話風格：

        參考對話範例：

"""


REMINDER = """切記,請模仿口氣但內容須對應粉絲的提問,避免死板複製。回覆盡量大約三句話以下,偶爾可以超過一點,
        如果發現話範例與本次對話無關,請不要強行將內容加入回復。
        不要直接提到這些範例,當作是自己的即興對話。
        要保持禮貌、莊重。"""

        
    
def get_chat_respond(message, image_base64, chat_history=""):
    bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name="ap-southeast-2"
        )
        
    # Construct the prompt
    system_prompt = PERSONALITY_PROMPT
    system_prompt += "請以偶像身分對這圖片作出回應。"
    system_prompt += "注意!請在尊重個人資料的情況下對人物進行描述。"
    system_prompt += "請身為一個風趣的人進行人性的對話,不要使用emoji"
    system_prompt += REMINDER
    
    user_prompt = ""
    # Add chat history if provided
    if chat_history:
        user_prompt += "以下是之前的聊天記錄,請參考這些記錄來回應粉絲的訊息：\n"
        user_prompt += chat_history
        user_prompt += "\n"
    
    # Add user message
    user_prompt += "這是粉絲的訊息:"
    user_prompt += message
    
    # Prepare the request payload

    request_body={
        "schemaVersion": "messages-v1",
        "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": user_prompt
                        },
                        {
                            "image": {
                                "format": "jpeg",
                                "source": {
                                "bytes": image_base64
                                }
                            }
                        },
                    ]
                }
            ],
            "system": [
                {
                "text": system_prompt
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "topP": 0.9,
                "topK": 20,
                "temperature": 0.7
            }
        }

    native_request_payload = {
        "inputText": user_prompt,  # "你今日過點嗎?"
        "textGenerationConfig": {
            "maxTokenCount": 500,
            "temperature": 0.75
        }
    }

    # Add system prompt if you have one
    if system_prompt:
        native_request_payload["systemPrompt"] = system_prompt

    # Add image if provided
    if image_base64:
        native_request_payload["inputImage"] = image_base64
    
    # Call the model
    response = bedrock_runtime.invoke_model(
        modelId="arn:aws:bedrock:ap-southeast-2:701030859948:inference-profile/apac.amazon.nova-lite-v1:0",
        body=json.dumps(request_body)
    )
    print(f"response: {response}")
    
    
    # Process the response
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        response_body = response["body"].read().decode("utf-8")
        #print(f"response_body: {response_body}")
        #print("response_json")
        response_json = json.loads(response_body)
        #print(json.dumps(response_json, indent=2))
        respond_message = response_json['output']['message']['content'][0]['text']
        print(f"response_message from chat bot: {respond_message}")
        return respond_message
    else:
        return 'error'