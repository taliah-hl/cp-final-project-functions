import json
from lambda_function import lambda_handler

with open('test_event.json', 'r') as f:
    test_event = json.load(f)

response = lambda_handler(test_event, None)
print(response)
