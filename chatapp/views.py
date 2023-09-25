
from django.shortcuts import render
from django.http import JsonResponse
from chatapp.models import Comments, User
import requests
from collections import defaultdict
from gensim.models.keyedvectors import KeyedVectors
from sklearn.cluster import KMeans
import json
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from collections import defaultdict
#ここにGoogle Cloud Platformで入手したYoutubeDataAPIをそのまま入力
YT_API_KEY = "AIzaSyDpJkQseYjIeAA_9j2vUzY0qxK_c5ZvwoU"
# Word2Vecモデルを読み込む
word2vec_model_path = 'youtube_comments_model.model'
# 単語数の上限を設定
max_vocab = 10000
# クラスタ数を設定
n_clusters = 5
#==========☆ トップページ用関数 ☆==========
def index(request):
    return render(request, "chatapp/index.html")
#==========☆　YouTubeコメント欄取得動作テストページ用関数 ☆==========
# 動作確認用に一時的に作ったページです。
def getchattest(request):
    return render(request, "chatapp/getchattest.html")
# 文章のベクトルを計算するための関数
def sentence_vector(sentence, model):
    # 文章をスペースで分割し、各単語がWord2Vecモデルの語彙に存在するか確認
    words = [word for word in sentence.split() if word in model.wv.key_to_index]
    # もし文章にWord2Vecの語彙に存在する単語が一つもなければNoneを返す
    if len(words) == 0:
        return None
    # 存在する単語のベクトルの平均を計算して返す
    return sum(model.wv[word] for word in words) / len(words)
def cluster_data(data, word2vec_model_path, n_clusters):
    print("コメント:",data)
    # 各コメントのベクトルを計算前に、dataの要素数を確認
    print("変換前のコメント数:",len(data))
    # Word2Vecモデルをロード
    model = KeyedVectors.load(word2vec_model_path)
    print("モデルの単語数:",len(model.wv.index_to_key))
    # modelの確認
    #print(model.wv.index_to_key)
    
    """# 各コメントのベクトルを計算
    vectors = [sentence_vector(comment, model) for comment in data]
    # Noneを除外（Word2Vecの語彙に存在しないコメントを除外）
    vectors = [v for v in vectors if v is not None]"""
    
     # 各コメントのベクトルを計算
    vectors = []
    converted_comments = []
    for comment in data:
        vector = sentence_vector(comment, model)
        if vector is not None:
            vectors.append(vector)
            converted_comments.append(comment)
    
    vectors = np.array(vectors)
    if len(vectors) < 2:
        print("ベクトルが足りません")


    # 階層的クラスタリングを適用
    Z = linkage(vectors, method='ward', metric='euclidean')
    
    # クラスタリングの結果を取得
    cluster_labels = fcluster(Z, n_clusters, criterion='maxclust')

    # 各クラスタに所属するコメントを集めるための辞書
    cluster_to_comments = defaultdict(list)

    # クラスタのラベルとコメントを対応付けて辞書に追加
    for cluster_id, comment in zip(cluster_labels, converted_comments):
        cluster_to_comments[cluster_id].append(comment)
    
    return cluster_to_comments
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
