# Nove Inference Samlpe code
https://docs.aws.amazon.com/nova/latest/userguide/complete-request-schema.html
```json
{
  "system": [
    {
      "text": string
    }
  ],
  "messages": [
    {
      "role": "user", //first turn should always be the user turn
      "content": [
        {
          "text": string
        },
        {
          "image": {
            "format": "jpeg" | "png" | "gif" | "webp",
            "source": {
              "bytes": image // Binary array (Converse API) or Base64-encoded string (Invoke API)
            }
          }
        },
        {
          "video": {
            "format": "mkv" | "mov" | "mp4" | "webm" | "three_gp" | "flv" | "mpeg" | "mpg" | "wmv",
            "source": {
              // Option 1: Sending a S3 location 
              "s3Location": {
                "uri": string, // example: s3://my-bucket/object-key
                "bucketOwner": string // (Optional) example: "123456789012"
               }
              // Option 2: Sending file bytes 
              "bytes": video // Binary array (Converse API) or Base64-encoded string (Invoke API)
            }
          }
        },
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": string //prefilling assistant turn
        }
      ]
    }
  ],
 "inferenceConfig":{ // all Optional, Invoke parameter names used in this example
    "maxTokens": int, // greater than 0, equal or less than 5k (default: dynamic*)
    "temperature": float, // greater then 0 and less than 1.0 (default: 0.7)
    "topP": float, // greater than 0, equal or less than 1.0 (default: 0.9)
    "topK": int, // 0 or greater (default: 50)
    "stopSequences": [string]
  },
  "toolConfig": { // all Optional
        "tools": [
                {
                    "toolSpec": {
                        "name": string, //meaningful tool name (Max char: 64)
                        "description": string, //meaningful description of the tool
                        "inputSchema": {
                            "json": { // The JSON schema for the tool. For more information, see JSON Schema Reference
                                "type": "object",
                                "properties": {
                                    args;: { //arguments 
                                        "type": string, //argument data type
                                        "description": string //meaningful description
                                    }
                                },
                                "required": [
                                    string //args
                                ]
                            }
                        }
                    }
                }
            ],
   "toolChoice": {"auto":{}} //Amazon Nova models ONLY support tool choice of "auto"
    }
}
```


```json
{
  "schemaVersion": "messages-v1",
  "messages": [
    {
      "role": "user",
      "content": [
        {"text": "A camping trip"}
      ]
    }
  ],
  "system": [
    {
      "text": "Act as a creative writing assistant. When the user provides you with a topic, write a short story about that topic."
    }
  ],
  "inferenceConfig": {
    "maxTokens": 500,
    "topP": 0.9,
    "topK": 20,
    "temperature": 0.7
  }
}
```