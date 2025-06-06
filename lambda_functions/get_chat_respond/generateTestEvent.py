import json
import base64

def create_test_event():
    # Load audio file and convert to base64
    with open('user_prompt1_how_are_you.wav', 'rb') as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
    
    # Load image file and convert to base64
    with open('test_image.jpg', 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create test event
    test_event = {
        "audio": audio_data,
        "image_base64": image_data,
        "chat_history": []  # Empty chat history for first interaction
    }
    
    # Save to file for use in Lambda console
    with open('test_event.json', 'w') as f:
        json.dump(test_event, f)
    
    print("Test event created and saved to test_event.json")

create_test_event()
