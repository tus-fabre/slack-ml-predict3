#!/usr/bin/env python
# coding: utf-8
#
# [FILE] predict_covid19.py
#
# [DESCRIPTION]
#  新型コロナウィルス感染者数を予測するSlackアプリトップファイル
#
# [NOTES]
#

import os, sys
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
# .envファイルの内容を読み込見込む
load_dotenv()

# BOTトークンからアプリを初期化する
slack_token=os.environ.get("SLACK_BOT_TOKEN")
if slack_token == None:
    print("環境変数が設定されていません")
    sys.exit()
app = App(token=slack_token)

# アプリトークン
app_token = os.environ["SLACK_APP_TOKEN"]
# ローカルフォルダー
local_folder = os.environ.get("LOCAL_FOLDER")

# ここのパッケージは重いので、ここでロードする
from covid19_model import createPredictedImageFile
from utils.modal_view import modalView

#
# [EVENT] message
#
# [DESCRIPTION]
#  次のメッセージを受信したときのリスナー関数
#   Unhandled request ({'type': 'event_callback', 'event': {'type': 'message', 'subtype': 'file_share'}})
#
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

#
# [SLASH COMMAND] /covid19_predict
#
# [DESCRIPTION]
#  スラッシュコマンド/covid19_predictのリスナー関数
#  指定した国（英語名）の一年の感染者実数と感染者予測結果をグラフで表現する
#
# [NOTES]
#  国名を指定しないとモーダルビューで注意を促す
#
@app.command("/covid19_predict")
def message_predict(ack, command, respond, body, client):
    ack()
    
    # 引数を取得する
    country = command["text"]

    # 引数が指定されていない場合、モーダルビューで警告する
    if country == '':
        viewObj = modalView("注意", "引数として英語国名を指定してください")
        client.views_open(trigger_id=body["trigger_id"], view=viewObj)
        return

    # 出力するパス名を準備する
    epoch_time = time.time()
    file_name = country + "-" + str(epoch_time) + ".png"
    file_path = local_folder + "/" + file_name
    
    # 360日のデータを使って、感染者数グラフファイルを生成する
    status = createPredictedImageFile(country, 360, file_path)
    if status == False:
        respond(f"画像ファイルを作成できませんでした")
        return
    
    print("[CREATED FILE] " + file_path)
    
    # 画像ファイルをアップロードする
    channel_id = body.get('channel_id')
    try:
        client.files_upload_v2(
            channel=channel_id,
            title="Generated - " + file_name,
            file=file_path,
            initial_comment="結果ファイルを添付します",
        )
        os.remove(file_path)
    except Exception as e:
        print(e)

#
# Start the Slack app
#
if __name__ == "__main__":
    print('⚡️Prediction App starts...')
    SocketModeHandler(app, app_token).start()

#
# END OF FILE
#