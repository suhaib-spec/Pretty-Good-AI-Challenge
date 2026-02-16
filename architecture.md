I built this system using Flask for the backend API because it's lightweight and perfect for handling webhooks from Retell. Python made sense since it's quick to prototype with and has great libraries for HTTP requests.

For the voice AI, I used Retell because they provide the entire voice infrastructure out of the box - speech-to-text, text-to-speech, and phone calling. Retell also supports function calling, which lets the bot log issues during conversations, and webhooks to send transcripts after calls end.

I store data in two formats - JSON and plain text. JSON gives structured data that can be queried programmatically, while text files let me quickly read logs in any editor without parsing. Both are file-based so there's no database to set up for this MVP.

The flow is simple: I schedule a batch call on Retell, Retell's bot makes the call and simulates a patient, the bot logs any issues it finds, and when the call ends Retell sends the full transcript via webhook. Everything gets saved to log format automatically.

Any changes I need to make to test the demo hotline even more. I just make changes to the bot's prompt set-up and place more batch calls. While keeping my flask server and ngrok tunnelling running ofcourse :)