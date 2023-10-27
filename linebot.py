from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import (MessageEvent,
                            TextMessage,
                            TextSendMessage, 
                            FlexSendMessage)

import openai
import json

openai.api_key = "xxx"
model_use = "text-davinci-003"

channel_secret = "xxx"
channel_access_token = "xxx"

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

app = Flask(__name__)
field = ""
prevQuestion = "this is the qus"

def startText():
    with open('welcomePageFlex.json') as user_file:
      file_contents = user_file.read()
    flex = json.loads(file_contents)
    replyObj= FlexSendMessage(alt_text='Career Choices', contents = flex)
    return replyObj


@app.route("/", methods=["GET","POST"])
def home():
    try:
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        handler.handle(body, signature)
    except Exception as e:
        print(e)
    
    return "Hello Line Chatbot"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    global field
    global prevQuestion
    newQuestion = 0
    text = event.message.text
    if "/start" in text:
        line_bot_api.reply_message(event.reply_token, startText())
    else:
        prompt_text = ""
        if "I would like to be" in text:
            prompt_text_array = text.split()
            for i in range(6,len(prompt_text_array)):
                prompt_text = prompt_text + prompt_text_array[i] + " "
            field = prompt_text
            prompt_text = "What will they test me on during a " + field + "interview?"
            print(prompt_text)
        elif "/job" in text:
            prompt_text_array = text.split()
            for i in range(1,len(prompt_text_array)):
                prompt_text = prompt_text + prompt_text_array[i] + " "
            field = prompt_text
            prompt_text = "What will they test me on during a " + field + "interview?"
            print(prompt_text)
        elif "/questions" in text:
            prompt_text = "Give me a tough and specific interview question for " + field
            newQuestion = 1
            print(prompt_text)
        elif "/next" in text: 
            prompt_text = "Give me another tough and specific interview question for " + field
            newQuestion = 1
            print(prompt_text)
        elif "/answer" in text:
            prompt_text = "Give me the answer to this question: " + prevQuestion
            print(prompt_text)
        else: 
            prompt_text = "for this question: " + prevQuestion +", why is this answer correct or wrong (if it is wrong, tell me why I am wrong without giving me the correct answer):" + text 
            print(prompt_text)
        response = openai.Completion.create(
        model=model_use,
        prompt=prompt_text,  
        max_tokens=1024,
        temperature = 0.5) 
        text_out = response.choices[0].text 
        if newQuestion: 
            prevQuestion = text_out
        print(prevQuestion)
        line_bot_api.reply_message(event.reply_token,
                                    TextSendMessage(text=text_out)) 


if __name__ == "__main__":          
    app.run(host="0.0.0.0",port=5001)

