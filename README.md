# AIDoll - CP Team 12 Final Project

This repository contains code for our final project, which demonstrates the use of AWS Lambda functions and a Raspberry Pi script for the AIDoll project.

## Structure

- **rpi/**: Main code and modules for the Raspberry Pi.
- **lambdas/**: Source code for all AWS Lambda functions, each in its own subfolder.
- **utils/**: Utility scripts used by the project.
- **test/**: Test data and scripts for local or Lambda testing.

## Lambda Functions

Each Lambda function is organized in its own folder under `lambdas/`:
- `cue/`: Handles cue start events.
- `cue_stop/`: Handles cue stop events.
- `get_chat_respond/`: Processes audio/image and generates chatbot responses.
- `health_check/`: Simple health check endpoint.
- `notify/`: Sends notifications via IoT.
- `text_to_speech/`: Converts text responses to speech.
```
.
cp-final-project-functions/
├── README.md
├── lambda_functions/     <--- All AWS Lambda Functions
│   ├── cue/
│   │   └── lambda_function.py
│   ├── cue_stop/
│   │   └── lambda_function.py
│   ├── get_chat_respond/
│   │   ├── audioTranscriber.py
│   │   ├── chatBot.py
│   │   ├── generateTestEvent.py
│   │   ├── lambda_function.py
│   │   └── testLambda.py
│   ├── health_check/
│   │   └── lambda_function.py
│   ├── notify/
│   │   └── lambda_function.py
│   └── text_to_speech/
├── rpi/
│   └── piMain.py          <----- main code on R Pi
├── ... # other files

```
## Raspberry Pi

The main script for the Raspberry Pi is in `rpi/piMain.py`. It connects to AWS IoT, listens for commands, and interacts with IoTCore and API gateway.

