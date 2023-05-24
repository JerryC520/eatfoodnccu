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
#line_bot_api = LineBotApi('M4OG1eV3C42zxSZOa2jX/IcDHVyF2neZ1BFWqjHU7kblxEIVAOcVyx3hxIRwen0wBL3sxpFgouCC1D5Kk3iStiMddLJCYCbzTWkhCWAmScs0NLeGMIaELYMw9cXCwRKC+VJaP8xWjfq3netQ5H+llwdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('17104e2c81c14ccb9a7ba4c629fe0cd1')

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

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

def recommend_top_10_by_score(df, rankbase):
    # 根據綜合評分排序，取前十名
    top_10 = sorted(df, key=lambda x: x[rankbase], reverse=True)[:10]
    response = "\n".join([f"餐廳名稱: {rest['Name']}\n分數: {rest[rankbase]}\n種類:{rest['type']}\n" for rest in top_10])
    return response

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == "綜合排名十大高評價餐廳":
        reply_text = recommend_top_10_by_score(df, 'rate_rank_score')
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))
        return
    if text == "綜合排名十大鄰近餐廳":
        reply_text = recommend_top_10_by_score(df, 'dist_rank_score')
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))
        return
    if text == "綜合排名十大高人氣餐廳":
        reply_text = recommend_top_10_by_score(df, 'pop_rank_score')
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))
        return    
    types = df.copy()
    istyped = True
    if ("中式" in text) or ("中國" in text):
        types = df[df['type'] == '中式料理'].copy()
    elif "亞洲" in text:
        types = df[df['type'] == '亞洲料理'].copy()
    elif "印度" in text:
        types = df[df['type'] == '印度料理'].copy()
    elif ("台灣" in text) or ("台式" in text) or ("台菜" in text) or ("小吃" in text):
        types = df[df['type'] == '台灣小吃/台菜'].copy()
    elif "咖啡" in text:
        types = df[df['type'] == '咖啡廳'].copy()
    elif "墨西哥" in text:
        types = df[df['type'] == '墨西哥料理'].copy()
    elif ("德式" in text) or ("德國" in text):
        types = df[df['type'] == '德國料理'].copy()
    elif  ("日式" in text) or ("日本" in text):
        types = df[df['type'] == '日式料理'].copy()
    elif "早午餐" in text:
        types = df[df['type'] == '早午餐'].copy()
    elif "早餐" in text:
        types = df[df['type'] == '早餐店'].copy()
    elif ("法式" in text) or ("法國" in text):
        types = df[df['type'] == '法式料理'].copy()
    elif ("泰式" in text) or ("泰國" in text):
        types = df[df['type'] == '泰式料理'].copy()
    elif "火鍋" in text:
        types = df[df['type'] == '火鍋'].copy()
    elif "燒烤" in text:
        types = df[df['type'] == '燒烤'].copy()
    elif "牛排" in text:
        types = df[df['type'] == '牛排'].copy()
    elif ("美式" in text) or ("美國" in text):
        types = df[df['type'] == '美式料理'].copy()
    elif ("義式" in text) or ("義大利" in text):
        types = df[df['type'] == '義式料理'].copy()
    elif ("英國" in text) or ("英式" in text):
        types = df[df['type'] == '英式料理'].copy()
    elif ("越式" in text) or ("越南" in text):
        types = df[df['type'] == '越式料理'].copy()
    elif "酒吧" in text:
        types = df[df['type'] == '酒吧'].copy()
    elif "鐵板燒" in text:
        types = df[df['type'] == '鐵板燒'].copy()
    elif "非洲" in text:
        types = df[df['type'] == '非洲料理'].copy()
    elif ("韓式" in text) or ("韓國" in text):
        types = df[df['type'] == '韓式料理'].copy()
    elif "餐酒" in text:
        types = df[df['type'] == '餐酒館'].copy()
    else:
        istyped = False

    if ("分數" in text) or ("評價" in text) or ("星星" in text) or ("最棒" in text) or ("最好" in text) or ("好吃" in text):
        restaurant = types.loc[types['rate_rank_score'].idxmax()]
    elif ("歡迎" in text) or ("人氣" in text) or ("評論" in text) or ("多人" in text) or ("熱度" in text):
        restaurant = types.loc[types['pop_rank_score'].idxmax()]
    elif ("政大" in text) or ("近" in text) or ("不遠" in text) or ("不要太遠" in text) or ("懶得走" in text):
        restaurant = types.loc[types['dist_rank_score'].idxmax()]
    else:
        if istyped:
            restaurant = types.loc[types['rate_rank_score'].idxmax()]    
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="對不起，我不明白您的問題。"))
            return
    
    if istyped:
        reply_text = f"以下是我所推薦的{restaurant['type']}優質餐廳:\n{restaurant['Name']}\n地址: {restaurant['Address']}\n電話: {restaurant['Phone']}\n種類: {restaurant['type']}"
    else:
        reply_text = f"以下是我所推薦的優質餐廳:\n{restaurant['Name']}\n地址: {restaurant['Address']}\n電話: {restaurant['Phone']}\n種類: {restaurant['type']}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))

# 打開request
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
