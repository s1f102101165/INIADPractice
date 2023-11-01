
from django.shortcuts import render
from django.http import JsonResponse
from chatapp.models import Comments, User
import requests
from collections import defaultdict
import datetime
from sklearn.cluster import KMeans
import numpy as np
from gensim.models import FastText
import fasttext
import os
import MeCab

#ここにGoogle Cloud Platformで入手したYoutubeDataAPIをそのまま入力
YT_API_KEY = "AIzaSyCbFs1IMNqYp_Y-kTA442GODM9g5DOmrF4"
# モデルを読み込む
model_path = "crawl-300d-2M-subword_part_aa"
fasttext_model = fasttext.load_model(model_path)
n_clusters = 3


#==========☆ トップページ用関数 ☆==========
def index(request):
    return render(request, "chatapp/index.html")


#==========☆ チャット取得本番ページ用関数 ☆==========
def chat(request):
    return render(request, "chatapp/chat.html")


#==========☆　YouTubeコメント欄取得動作テストページ用関数 ☆==========
# 動作確認用に一時的に作ったページです。
def getchattest(request):
    return render(request, "chatapp/getchattest.html")
def cluster_data(comments, fasttext_model):
    vectorized_comments = []
    vector_dim = fasttext_model.get_dimension()  # ベクトルの次元数を取得
    tagger = MeCab.Tagger("-Owakati") # 文字列を単語に区切るルールを指定
    for comment in comments:
        space_sentence = tagger.parse(comment) # コメントの文字列を単語ごとにスペースで区切る
        words = space_sentence.split()  # 簡単にスペースで単語を分割
        vectors = [fasttext_model.get_word_vector(word) for word in words]
        if vectors:
            avg_vector = sum(vectors) / len(vectors)
        else:
            avg_vector = [0] * vector_dim
        vectorized_comments.append(avg_vector)
    
    if vectorized_comments:  # vectorized_commentsが空でないことを確認
        kmeans = KMeans(n_clusters=min(n_clusters, len(vectorized_comments)), n_init=10, verbose=1, random_state=42).fit(vectorized_comments)
    else:
        print("No comments were vectorized.")
    labels = kmeans.labels_
    print("[", labels, "]")
    clustered_comments = {}
    for i, label in enumerate(labels):
        if label not in clustered_comments:
            clustered_comments[label] = []
        clustered_comments[label].append(comments[i])
    return clustered_comments, labels


# 動画タイトル取得用関数
def api_getmovie(request):
    video_id = request.GET["youtubeurl"]
    api_key = YT_API_KEY

    url = 'https://www.googleapis.com/youtube/v3/videos'
    api_key = YT_API_KEY
    # APIに渡すパラメータを設定
    params = {
        'key': api_key,
        'part': 'snippet',
        'id': video_id,
    }

    # YouTube APIを呼び出し、結果をJSONとして取得
    response_data = requests.get(url, params=params).json()
    
    return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False}, safe=False)


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
    result = get_chat(video_id, nextPageToken, api_key)
    # DBからコメント抽出
    newdata = list(choose_comment().values())

    # エラーが出てうまく動いていないならコメントではなくエラーを返す
    if ("errorcode" in result):
        newdata = result

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
        return {"errorcode":response_data['error']['message']}  # ここでは空のリストを返すことを例としています
    # エラーがない場合、通常の処理を続行
    # 取得したデータからコメントの内容のみをリストとして抽出
    comments = [item["snippet"]["displayMessage"] for item in response_data["items"]]
    print("なかみ",comments)
    # 抽出したコメントをクラスタリング
    clustered_comments, clustered_labels = cluster_data(comments, fasttext_model)  
    print("クラスタリング:",clustered_comments)
    # nextPageTokenを設定
    userobj = User.objects.get(pk=1)
    userobj.nextPageToken = response_data["nextPageToken"]
    userobj.save()

    # クラスタリング結果を元のコメントと


    # クラスタリング結果をデータベースに保存
    input_database(clustered_labels, response_data["items"])
    return {}


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
    if 'items' not in data:
        print("No items found in data.")
        return None
    
    try:
        liveStreamingDetails = data['items'][0]['liveStreamingDetails']
        chat_id = liveStreamingDetails['activeLiveChatId']
    except :
        chat_id = None
        print("[views.pyのget_chat_id関数からのお知らせ]\n何かしらの問題によりチャットidが取得できませんでした。\nAPIキーの間違いや、動画URLの間違いなどが考えられます\n（ライブ配信でない動画や、ライブ配信のアーカイブのチャット欄は取得できません。）\n")
    

    return chat_id


# コメントをデータベースに格納する関数
def input_database(labels, all_comments):

    already_labels = [] #登場したラベルを格納していくリスト

    # 全部のコメントを取り出し、格納
    for i in range(len(all_comments)):
        new_body = all_comments[i]["snippet"]["displayMessage"]
        new_posted_at = datetime.datetime.strptime(all_comments[i]["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%S.%f%z") + datetime.timedelta(hours=9) #日本時間に合わせるため、文字列をdatetime型に変換したのち+9時間
        new_name = all_comments[i]["authorDetails"]["displayName"]
        new_userid = all_comments[i]["authorDetails"]["channelId"]
        new_cluster_label = labels[i]
        new_cluster_display = not (new_cluster_label in already_labels) # 初めてのラベルなら表示ON、そうでないなら表示OFF

        # 表示ONならこのラベル初登場なので、登場したラベルリストに加えておく
        if (new_cluster_display):
            already_labels.append(new_cluster_label)

        comment = Comments(body = new_body, posted_at = new_posted_at, name = new_name, userid = new_userid, cluster_label = new_cluster_label, cluster_display = new_cluster_display)
        comment.save()
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
    return Comments.objects.all().filter(cluster_display=True).order_by("-posted_at")[:50] #表示ONなものだけ新着順で抽出。filterのカッコ内にカンマ区切りで条件付け加え可能。
