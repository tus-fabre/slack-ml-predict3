#!/usr/bin/env python
# coding: utf-8
#
# [FILE] covid19_model.py
#
# [DESCRIPTION]
#  新型コロナウィルス感染者数予測にかかわる関数を定義するファイル
#
# [NOTES]
#
import os
import datetime
import requests

# 警告を無視する
import re
import warnings
warnings.filterwarnings('ignore')

# ライブラリを読み込む
import math
import pandas as pd
import numpy as np

# kerasのライブラリを読み込む
from keras.models import Sequential
from keras.layers import Dense, LSTM

# scikit-learnの正規を行うライブラリを読み込む
from sklearn.preprocessing import MinMaxScaler

# scikit-learnで決定係数とRMSEの計算を行うライブラリを読み込む
from sklearn.metrics import r2_score, mean_squared_error

# グラフ表示のライブラリとグラフ表示で日本語を表示するためのライブラリを読み込む
import matplotlib.pyplot as plt
import japanize_matplotlib

# disease.shにアクセスするためのベースURL
BASE_URL = os.environ.get("COVID19_BASE_URL")

#
# [FUNCTION] createPredictedImageFile()
#
# [DESCRIPTION]
#  新型コロナウィルスの新規感染者数の履歴と予測した感染者数の画像を作成する
# 
# [INPUTS]
#  country  - 対象となる国名
#  lastdays - 現在から何日前までの情報を取得するか日数を指定する。'all'のときはすべてのデータを対象とする
#  filename - 保存する画像ファイル名(フォルダ名を含む)
# 
# [OUTPUTS]
#  関数が成功すればtrue、失敗したらfalseを返す
#
# [NOTES]
#  lastdaysで指定した日数のうち80%がトレーニング、20%が評価に用いられる
#  機械学習には、Long Short-Term Memory layerに基づく、時系列データに対するモデルを用いる
#
def createPredictedImageFile(country, lastdays, filename):
  # 出力用の変数を初期化
  dateL  = []
  caseL  = []
  deathL = [] # 利用しない
  status = getHistoricalData(country, str(lastdays), dateL, caseL, deathL)
  if status == False:
    return False
  
  # データフレームを作成する
  df = pd.DataFrame(
    index=np.array(dateL),
    data={'Cases': np.array(caseL)}
  )
  print(df)

  # 取得した新型コロナデータの感染者数をdatasetに代入する
  dataset = df.values

  # 最小値->0、最大値->1となるように正規化する
  scaler = MinMaxScaler(feature_range=(0, 1))
  scaled_data = scaler.fit_transform(dataset)

  # 取得したデータの8割を訓練データとする
  # math.ceil : 小数点以下を切り上げ
  training_data_len = math.ceil(len(dataset) * .8)
  # 正規化したデータから訓練で使用する行数分のデータを抽出する
  train_data = scaled_data[0:training_data_len, :]

  # 訓練データと正解データを保存する配列を用意する
  x_train = [] # 訓練データ
  y_train = [] # 正解データ

  # 訓練データとして60日分のデータをx_train[]に追加する
  # 正解データとして61日目のデータをy_train[]に追加する
  for i in range(60, len(train_data)):
    x_train.append(train_data[i - 60:i, 0])
    y_train.append(train_data[i, 0])

  # Convert the x_train and y_train to numpy arrays
  # 訓練データと教師データをNumpy配列に変換する
  x_train, y_train = np.array(x_train), np.array(y_train)

  # 訓練データのNumpy配列について、奥行を訓練データの数、行を60日分のデータ、
  # 列を1、の3次元に変換する
  x_train_3D = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

  # LSTMモデルを定義する
  n_hidden = 50 # 隠れ層の数
  units1 = 25   # 第1層の出力数
  units2 = 1    # 第2層の出力数

  model = Sequential()
  model.add(LSTM(n_hidden, return_sequences=True, input_shape=(x_train_3D.shape[1], 1)))
  model.add(LSTM(n_hidden, return_sequences=False))
  model.add(Dense(units1))
  model.add(Dense(units2))

  # 定義したLSTMモデルをコンパイルする
  # 最適化手法: adam
  # 損失関数:   最小2乗誤差
  model.compile(optimizer='adam', loss='mean_squared_error')

  # コンパイルしたモデルの学習を行う
  batch_size = 1  # バッチサイズ
  epochs = 1      # 訓練の回数
  model.fit(x_train_3D, y_train, batch_size=batch_size, epochs=epochs)

  # 検証データを用意する(60日分)
  test_data = scaled_data[training_data_len - 60:, :]

  # x_test:検証データ
  # y_test:正解データ
  x_test = []
  y_test = scaled_data[training_data_len:, :]

  # 検証データをセットする
  for i in range(60, len(test_data)):
    x_test.append(test_data[i - 60:i, :])

  # 検証データをNumpy配列に変換する
  x_test = np.array(x_test)

  # 検証データのNumpy配列について、奥行を訓練データの数、行を60日分のデータ、列を1、の3次元に変換する
  x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

  # モデルに検証データを代入して予測を行う
  predictions = model(x_test)

  # 予測データをNumpy配列に変換する
  predictions = np.array(predictions)

  # モデルの精度を評価する
  # 決定係数とRMSEを計算する
  # 決定係数は1.0に、RMSEは0.0に近いほど、モデルの精度は高い
  score = r2_score(y_test, predictions)
  rmse = np.sqrt(mean_squared_error(y_test, predictions))
  print(f'r2_score: {score:.4f}')
  print(f'rmse: {rmse:.4f}')

  # 予測データは正規化されているので、元の感染者数に戻す
  predictions = scaler.inverse_transform(predictions)

  # 実際の感染者数、予測の感染者数をグラフで表示する
  valid = df[training_data_len:]
  valid['Predictions'] = predictions

  # グラフを表示する領域をfigとする
  fig = plt.figure(figsize=(12,8))

  # 領域のどこを使用するかを設定する
  # 1行 x 1列のグリッド、最初のサブプロット(1)
  ax = fig.add_subplot(111)

  # グラフを設定する
  title = '感染者数の履歴と予測結果 (' + country + ')'
  ax.set_title(title, fontsize=18)
  ax.set_xlabel('日付', fontsize=12)
  ax.set_ylabel('感染者数 (人)', fontsize=12)
  ax.plot(df['Cases'])
  ax.plot(valid[['Predictions']])
  ax.legend(['実際の数', '予測の数'], loc='upper left') # 凡例
  ax.grid()

  # 画像を保存する
  fig.savefig(filename)
  #plt.show()
  
  return True

#
# [FUNCTION] getHistoricalData()
#
# [DESCRIPTION]
#  指定した日数分の新型コロナウィルスの新規感染者数と死亡者数を取得する
# 
# [INPUTS]
#  country  - 対象となる国名
#  lastdays - 今日から何日前までの情報を取得するか日数を指定する。'all'のときはすべてのデータを対象とする。
# 
# [OUTPUTS]
#  次の出力用引数には初期設定として空リストを関数に与えておく
#  dateL  - 日付のリスト
#  caseL  - 新規感染者数のリスト
#  deathL - 死亡者数のリスト
#  
#  関数が成功すればtrue、失敗したらfalseを返す
# 
# [NOTES]
#  アクセスするURL
#    https://disease.sh/v3/covid-19/historical/<Country>?lastdays=<日数 or all>
#
#  countryがallの場合,　結果の直下にcasesとdeathsのキーが存在する。
#  それ以外の場合、結果の下にtimelineが現れ、その下にcasesとdeathsのキーが存在する。
#
def getHistoricalData(country, lastdays, dateL, caseL, deathL):
  status = False

  if country == "":
    return status

  url = BASE_URL + "historical/" + country + "?lastdays=" + lastdays
  print(url)
  result = requests.get(url)
  if result.status_code == 200:
    json = result.json() # JSONに変換する
    
    # 新たな感染者数を前日との差分として集める
    if country == 'all':
      cases = json["cases"]
    else:
      cases = json["timeline"]["cases"]
      
    previous_value = -1
    for key in cases: # keyは日付：m/d/YY
      num_cases = int(cases[key])
      if previous_value >= 0:
        date_value = convertDateFormat(key) # M/D/YY -> YYYY-MM-DD
        dateL.append(date_value)
        caseL.append(num_cases-previous_value)
      previous_value = num_cases

    # 新たな死亡者数を前日との差分として集める
    if country == 'all':
      deaths = json["deaths"]
    else:
      deaths = json["timeline"]["deaths"]
      
    previous_value = -1
    for key in deaths:
      num_deaths = int(deaths[key])
      if previous_value >= 0:
        deathL.append(num_deaths-previous_value)
      previous_value = num_deaths
      
    status = True
      
  return status

#
# [FUNCTION] convertDateFormat()
#
# [DESCRIPTION]
#  https://disease.shが返す日付形式を標準形式に変換する
# 
# [INPUTS]
#  date  - 変換対象の日付（M/D/YY形式の文字列）
# 
# [OUTPUTS]
#  Dateオブジェクト
#
def convertDateFormat(date):
  list = date.split('/')
  month = int(list[0])
  day = int(list[1])
  year = int("20" + list[2]) # YY -> YYYY
  
  date_obj = datetime.date(year, month, day)
  
  #return date_obj.strftime('%Y-%m-%d')
  return date_obj
  
#
# END OF FILE
#