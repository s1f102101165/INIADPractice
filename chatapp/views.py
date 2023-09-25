
from django.shortcuts import render
from django.http import JsonResponse
from chatapp.models import Comments, User
import requests
from collections import defaultdict
import json
from sklearn.cluster import KMeans
import numpy as np
from gensim.models import Word2Vec

#learning.pyをimport
from learning import *

#ここにGoogle Cloud Platformで入手したYoutubeDataAPIをそのまま入力
YT_API_KEY = "AIzaSyDpJkQseYjIeAA_9j2vUzY0qxK_c5ZvwoU"
# Word2Vecモデルを読み込む
word2vec_model_path = 'youtube_comments_model.model'
# 単語数の上限を設定
max_vocab = 10000

n_clusters = 5

#==========☆ トップページ用関数 ☆==========
def index(request):
    return render(request, "chatapp/index.html")
#==========☆　YouTubeコメント欄取得動作テストページ用関数 ☆==========
# 動作確認用に一時的に作ったページです。
def getchattest(request):
    return render(request, "chatapp/getchattest.html")

def vectorize_comments(comments, model):
    vectorized_comments = []
    
    for comment in comments:
        words = comment.split()
        vectors = [model.wv[word] for word in words if word in model.wv]
        
        if vectors:
            vectorized_comments.append(np.mean(vectors, axis=0))
        else:
            vectorized_comments.append(np.zeros(model.vector_size))
    
    return vectorized_comments

def cluster_data(data, word2vec_model_path, n_clusters=n_clusters):
    # Word2Vecモデルのロード
    model = Word2Vec.load(word2vec_model_path)
    
    # 各コメントをベクトルに変換
    X = vectorize_comments(data, model)

    # 実際のクラスタリング
    km_model = KMeans(n_clusters=n_clusters)
    if len(X) == 0:
        return []
    km_model.fit(X)
    labels = km_model.labels_

    # クラスタごとにコメントを格納するリスト
    clustered_comments_list = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
        clustered_comments_list[label].append(data[idx])

    return clustered_comments_list

# コメント取得をテストページで使えるようにAPI化したもの
def api_getchat(request):
    # トークンを取得
    nextPageToken = User.objects.get(pk=1).nextPageToken
    # api_reset()を実行するとUser.objects.get(pk=1).nextPageToken = 0になるので、リセットされたらトークンもNoneにする
    if (nextPageToken == "0"):
        nextPageToken = None
    video_id = request.GET["youtubeurl"]
    # APIキーを取得
    api_key = YT_API_KEY
    # get_chat()関数を呼び出して、コメントデータを取得
    # ここでAPIキーを渡すように変更
    clustered_comments = get_chat(video_id, nextPageToken, api_key)
    # DBからコメント抽出
    newdata = list(choose_comment().values())
    return JsonResponse(newdata, json_dumps_params={'ensure_ascii': False}, safe=False)
# データベースリセット用API
def api_reset(request):
    reset_database()
    return JsonResponse({})
#==========☆　YouTubeコメント欄取得関数 ☆==========
MAX_GET_CHAT = 100 #1度の取得最大数
# YouTubeのチャットを取得する関数
def get_chat(video_id, pageToken, api_key):
    # video_idからchat_idを取得する関数（以前の部分で提供されていたと思われる）
    chat_id = get_chat_id(video_id)
    # YouTube APIのエンドポイント
    url = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
    api_key = YT_API_KEY
    # APIに渡すパラメータを設定
    params = {
        'key': api_key,
        'liveChatId': chat_id,
        'part': 'id,snippet,authorDetails',
        'maxResults': MAX_GET_CHAT
    }
    # pageTokenが文字列として提供された場合、それをパラメータに追加
    if type(pageToken) == str:
        params['pageToken'] = pageToken
    # YouTube APIを呼び出し、結果をJSONとして取得
    response_data = requests.get(url, params=params).json()

    # APIの応答に 'error' キーが存在する場合、エラーハンドリングを行う
    if 'error' in response_data:
        print("Error from YouTube API:", response_data['error']['message'])
        # 必要に応じて、その他のエラーハンドリング処理を追加
        return []  # ここでは空のリストを返すことを例としています

    # エラーがない場合、通常の処理を続行
    comments = [item["snippet"]["displayMessage"] for item in response_data["items"]]
    print("なかみ",response_data)

    # 取得したデータからコメントの内容のみをリストとして抽出
    comments = [item["snippet"]["displayMessage"] for item in response_data["items"]]
    
    # 抽出したコメントをクラスタリング
    clustered_comments = cluster_data(comments, word2vec_model_path, n_clusters)
    
    # nextPageTokenを設定
    userobj = User.objects.get(pk=1)
    userobj.nextPageToken = response_data["nextPageToken"]
    userobj.save()
    # クラスタリング結果をデータベースに保存
    input_database(clustered_comments)
    return

def view_comments(request):
    # データベースからコメントを取得
    comments = Comments.objects.all().order_by("-posted_at")[:50]
    context = {
        "comments": comments
    }
    return render(request, "chatapp/getchattest.html", context)
# ChatのIDを取得する関数(チャットを取得する関数本体で使用)
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
# をデータベースに格納する関数
def input_database(data):
        
    for i in range(len(data)):
        new_body = data[i][i]
        new_posted_at = "2023-08-17T07:22:48.541037+00:00"
        comment = Comments(body = new_body, posted_at = new_posted_at)
        comment.save()
    return


# 【今は使っていないですが後で使うかもしれないので一応残しておきます】旧ver 取得したコメントをデータベースに格納する関数
def input_old_database(data):
    if ("pageInfo" in data):
        chat_num = data['pageInfo']['resultsPerPage']
        
        
        for i in range(chat_num):
            new_body = data["items"][i]["snippet"]["displayMessage"]
            new_name = data["items"][i]["authorDetails"]["displayName"]
            new_userid = data["items"][i]["authorDetails"]["channelId"]
            new_posted_at = data["items"][i]["snippet"]["publishedAt"]
            comment = Comments(body = new_body, name = new_name, userid = new_userid, posted_at = new_posted_at)
            comment.save()
        userobj = User.objects.get(pk=1)
        userobj.nextPageToken = data["nextPageToken"]
        userobj.save()
    return
# 取得したコメントをリセット。全部消す関数。
def reset_database():
    for comment in Comments.objects.all():
        comment.delete()
    try:
        userobj = User.objects.get(pk=1)
        userobj.nextPageToken = "0"
        userobj.save()
    except:
        userobj = User(nextPageToken = "0")
        userobj.save()
    return
#==========☆　コメントデータベースからコメントを抜粋する関数 ☆==========
def choose_comment():
    return Comments.objects.all().order_by("-posted_at")[:50]
