# slack-ml-predict3

## Slack APIによるプログラミング　機械学習への応用編

Slack APIチュートリアル「NodeJSとSlack APIによるいまどきのネットワークプログラミング」の応用編として機械学習向けにアプリを公開する。

### Webサービスから認識する

新型コロナウイルス感染者数の履歴から感染者数を予測し、結果をグラフ表示する。

#### 必要なライブラリをインストールする

>$ pip install -r requirements.txt

#### 環境変数を設定する

- ファイルenv.tpl内のSLACK_BOT_TOKEN、SLACK_APP_TOKEN、SLACK_USER_TOKENに該当するトークン文字列を設定する
- env.tplをenv.batに名前を変え、バッチを実行する
  >$ ren env.tpl env.bat
  >
  >$ env.bat

#### 新型コロナウィルス感染者数を予測する

- 過去の感染者数履歴から感染者数を予測し、結果をグラフ表示する
- 起動方法
  >$ python predict_covid19.py
- スラッシュコマンド/covid19_predict <国名>を起動する
  >例 /covid19_predict Japan
- 指定した国の一年の感染者実数と直近60日間の感染者予測数がグラフとしてアップロードされることを確認する
