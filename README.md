# slack-ml-predict3

## Slack APIによるプログラミング　機械学習への応用編

Slack APIチュートリアル「NodeJSとSlack APIによるいまどきのネットワークプログラミング」の応用編として機械学習向けにアプリを公開する。

### Webサービスから認識する

新型コロナウイルス感染者数の履歴から感染者数を予測し、結果をグラフ表示する。

#### 必要なパッケージをインストールする

コマンドライン上で次のコマンドを起動し、依存するPythonパッケージをインストールする。

```bash
pip install -r requirements.txt
```

#### 環境変数を設定する

本アプリを起動するには環境変数の設定が必要である。env.tplファイルを環境変数設定ファイル.envとしてコピーし、以下の環境変数を定義する。

```bash
copy env.tpl .env
```

|  変数名  |  説明  |
| ---- | ---- |
|  SLACK_BOT_TOKEN  | Botユーザーとして関連付けられたトークン。対象Slackワークスペースのアプリ設定 > [OAuth & Permissions] > [Bot User OAuth Token]から取得する。xoxb-で始まる文字列。 |
|  SLACK_APP_TOKEN  | 全ての組織を横断できるアプリレベルトークン。対象Slackワークスペースのアプリ設定 > [Basic Information] > [App-Level Tokens]から取得する。xapp-で始まる文字列。 |
|  SLACK_USER_TOKEN  | アプリをインストールまたは認証したユーザーに成り代わってAPIを呼び出すことができるトークン。対象Slackワークスペースのアプリ設定 > [OAuth & Permissions] > [User OAuth Token]から取得する。xoxp-で始まる文字列。 |
|  COVID19_BASE_URL  | 新型コロナウィルス感染者情報を提供するWebサイト（REST API）のURL |
|  LOCAL_FOLDER  | Slackにアップロードしたファイルを暫定的に保存するローカルフォルダーの名前 |

#### 新型コロナウィルス感染者数を予測する

- 過去の感染者数履歴から感染者数を予測し、結果をグラフ表示する。
- 起動方法

```bash
python predict_covid19.py
```

- スラッシュコマンド **/covid19_predict <国名>** を起動する。
  >例 /covid19_predict Japan
- 指定した国の一年の感染者実数と直近60日間の感染者予測数がグラフとしてアップロードされることを確認する。

### 更新履歴

- 2025-06-16 dotenvを利用
- 2023-12-12 ファイルアップロードをfiles_upload_v2()に変更
- 2023-02-01 初版
