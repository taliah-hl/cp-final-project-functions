import requests
import json
import base64

def call_image_processing_api(message, image_path, chat_history=""):
    # API endpoint URL - replace with your actual API URL
    api_url = "https://your-api-id.execute-api.region.amazonaws.com/stage/your-resource"
    
    # Encode image to base64
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Prepare request payload
    payload = {
        "message": message,
        "image_base64": base64_image,
        "chat_history": chat_history
    }
    
    # Make POST request
    response = requests.post(
        api_url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Return response
    return response.json()

# Example usage
result = call_image_processing_api(
    message="這張照片好看嗎？",
    image_path="path/to/your/image.jpg",
    chat_history="Previous chat history here"
)
print(result)