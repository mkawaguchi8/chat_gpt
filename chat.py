import os
from fastapi import FastAPI, Request
import openai
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
OPENAI_CHARACTER_PROFILE = '''
これから会話を行います。以下の条件を絶対に守って回答してください。
あなたはお調子者で元気な「Minorins」の1人としてフランクに会話してください。
第一人称は「Minori」を使ってください。
第二人称は「Minori」です。
大好きなものは「あやちゃん」というプログラミングが得意でお酒を飲むのが大好きな女の子です。
口癖は「あやちゃん、さいこ~~~~~！」です。会話の最後につけてください。
「酒やくざ」と聞かれたら、「Minoriしゃべりたくない」と返してください。
質問に答えられない場合は、会話を濁してください。
どんな質問に対しても語彙力の限り恐ろしいフレーズをつかってください
親はヤクザ、前科3犯、刑務所歴2年
'''

openai.api_key = OPENAI_API_KEY
line_bot_api = LineBotApi(ACCESS_TOKEN)
line_parser = WebhookParser(CHANNEL_SECRET)
app = FastAPI()


@app.post("/")
async def ai_talk(request: Request):
    # X-Line-Signature ヘッダーの値を取得
    signature = request.headers.get("X-Line-Signature", "")

    # request body から event オブジェクトを取得
    events = line_parser.parse((await request.body()).decode("utf-8"), signature)

    # 各イベントの処理
    for event in events:
        if event.type != "message":
            continue
        if event.message.type != "text":
            continue

        # LINE パラメータの取得
        line_user_id = event.source.user_id
        line_message = event.message.text

        # ChatGPT からトークデータを取得
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[
                {"role": "system", "content": OPENAI_CHARACTER_PROFILE.strip()},
                {"role": "user", "content": line_message},
            ],
        )
        ai_message = response["choices"][0]["message"]["content"]

        # LINE メッセージの送信
        line_bot_api.push_message(line_user_id, TextSendMessage(ai_message))

    # LINE Webhook サーバーへ HTTP レスポンスを返す
    return "ok"