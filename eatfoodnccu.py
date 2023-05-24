import os
import pandas as pd
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# 設定你的Channel Access Token和Channel Secret
line_bot_api = LineBotApi('M4OG1eV3C42zxSZOa2jX/IcDHVyF2neZ1BFWqjHU7kblxEIVAOcVyx3hxIRwen0wBL3sxpFgouCC1D5Kk3iStiMddLJCYCbzTWkhCWAmScs0NLeGMIaELYMw9cXCwRKC+VJaP8xWjfq3netQ5H+llwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('17104e2c81c14ccb9a7ba4c629fe0cd1')

# 讀取CSV檔案
df = pd.read_csv('restaurant_data.csv')
df['rate_rank_score'] = 0.5*df['rating_score'] + 0.25*df['popularity'] + 0.25*df['distance_score']
df['pop_rank_score'] = 0.25*df['rating_score'] + 0.5*df['popularity'] + 0.25*df['distance_score']
df['dist_rank_score'] = 0.25*df['rating_score'] + 0.25*df['popularity'] + 0.5*df['distance_score']

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    print(text)
    if ("綜合分數" in text) or ("評價" in text):
        restaurant = df.loc[df['rate_rank_score'].idxmax()]
        print("rating")
    elif ("歡迎" in text) or ("人氣" in text) or ("評論" in text):
        restaurant = df.loc[df['pop_rank_score'].idxmax()]
        print("pop")
    elif ("鄰近" in text) or ("政大最近" in text):
        restaurant = df.loc[df['dist_rank_score'].idxmax()]
        print("dist")
    else:
        print("else")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="對不起，我不明白您的問題。"))
        return
    
    reply_text = f"以下是我所推薦:\n{restaurant['Name']}\n地址: {restaurant['Address']}\n電話: {restaurant['Phone']}\n種類: {restaurant['type']}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))

# 打開request
if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    app.run(host='127.0.0.1', port=port)
