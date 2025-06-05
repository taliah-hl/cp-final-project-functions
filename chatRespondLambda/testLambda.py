import requests
import json

def call_endpoint():
    # API endpoint URL
    endpoint_url = "https://cagrxdp7g5.execute-api.ap-southeast-2.amazonaws.com/get-chat-respond"
    
    # Load JSON data from file
    with open('test_event.json', 'r') as file:
        request_data = json.load(file)
    
    # Set headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Make the POST request
    print("Sending request to endpoint...")
    response = requests.post(endpoint_url, json=request_data, headers=headers)
    
    # Print response details
    print(f"Status Code: {response.status_code}")
    print("Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

if __name__ == "__main__":
    call_endpoint()
