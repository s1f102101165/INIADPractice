import django
from django.conf import settings

if not settings.configured:
    settings.configure(DEFAULT_SETTINGS_MODULE='INIADPractice.settings')
django.setup()

from django.shortcuts import render
from django.http import JsonResponse
#from chatapp.models import Comments, User
import requests
from collections import defaultdict
from gensim.models.keyedvectors import KeyedVectors
from sklearn.cluster import KMeans
import json
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from collections import defaultdict

YT_API_KEY = "AIzaSyDpJkQseYjIeAA_9j2vUzY0qxK_c5ZvwoU"
MAX_GET_CHAT = 100

def get_chat_id(video_id):
    url    = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YT_API_KEY, 'id': video_id, 'part': 'liveStreamingDetails'}
    data   = requests.get(url, params=params).json()
    if not data['items']:
        print("No items found in data.")
        return None
    
    liveStreamingDetails = data['items'][0]['liveStreamingDetails']
    if 'activeLiveChatId' in liveStreamingDetails.keys():
        chat_id = liveStreamingDetails['activeLiveChatId']
    else:
        chat_id = None
    return chat_id

def get_comments(video_id, api_key):
    # YouTube APIのエンドポイント
    url = 'https://www.googleapis.com/youtube/v3/commentThreads'
    # APIに渡すパラメータを設定
    params = {
        'key': api_key,
        'textFormat': 'plainText',
        'part': 'snippet',
        'videoId': video_id,
        'maxResults': 100
    }
    # YouTube APIを呼び出し、結果をJSONとして取得
    response_data = requests.get(url, params=params).json()
    # 取得したデータからコメントの内容のみをリストとして抽出
    comments = [item["snippet"]["topLevelComment"]["snippet"]["textDisplay"] for item in response_data["items"]]
    return comments


video_ids = ["1jFEhVWIQIM", "Tyeb5hnz0HM", "hsPghlQkLVs", "p-DU39snpvY", "IvRgHeJbhZI",
              "AqBOOcSK8Z8", "9DcPTHdU1T4", "XiSa_VIrGKE", "zuoVd2QNxJo", "ghCHZfPVUfk", 
              "hJ1H5bcvHtE", "GtIeq5n0sX0", "Hk2o-nCwdFQ", "QRFy2MNtqPQ", "MmG-vXNDeA8", "BeZMaLYqh5Q"]  # ここに動画IDを追加

all_comments = []

for video_id in video_ids:
    comments_video = get_comments(video_id,YT_API_KEY)
    all_comments.extend(comments_video)

def save_to_csv(data, filename):

    # リストをpandasのDataFrameに変換
    df = pd.DataFrame(data, columns=["コメント"])
    
    # CSVファイルに保存
    df.to_csv(filename, index=False)


save_to_csv(all_comments, "youtube_comments.csv")