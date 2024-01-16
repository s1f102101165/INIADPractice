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
import openai
import time

openai.api_key = "chHJM8Hh_9xSdUvtIKDyWgT9x8BOubw8AMXdvSyUBBEG4YzQMKtUI0Xi6x8Gx1N8Rcoamjl9tNxxmgY79Jaxwwg"
openai.api_base = "https://api.openai.iniad.org/api/v1"

#ここにGoogle Cloud Platformで入手したYoutubeDataAPIをそのまま入力
YT_API_KEY = "AIzaSyCMshRndIskgi-LUVTaApDHldVsvhv8aCY"
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


#==========☆YouTubeコメント欄取得動作テストページ用関数 ☆==========
# 動作確認用に一時的に作ったページです。
def getchattest(request):
    return render(request, "chatapp/getchattest.html")

# アンチコメント判定モード変更
def api_changeCommentFastMode(request):
    # nextPageTokenを設定
    userobj = User.objects.get(pk=1)
    userobj.commentFastMode = 1 - userobj.commentFastMode
    userobj.save()
    return JsonResponse({"result": "ok"})

# アンチコメントフィルターレベル変更
def api_changeCommentFileterLevel(request):

    # nextPageTokenを設定
    userobj = User.objects.get(pk=1)
    userobj.commentFilterLevel = int(request.GET["newLevel"])
    userobj.save()


    return JsonResponse({"result": "ok"})


def cluster_data(comments, fasttext_model):
    


    #print("Cluster Data - Comments:", comments)
    vectorized_comments = []
    vector_dim = fasttext_model.get_dimension()  # ベクトルの次元数を取得
    tagger = MeCab.Tagger("-Owakati") # 文字列を単語に区切るルールを指定
    for comment in comments:
        space_sentence = tagger.parse(comment) # コメントの文字列を単語ごとにスペースで区切る
        words = space_sentence.split()  # 簡単にスペースで単語を分割
        vectors = [fasttext_model.get_word_vector(word) for word in words]
        if vectors:
            avg_vector = sum(vectors) / len(vectors)
            for i in range(len(vectors)):
                print(words[i], ":", sum(vectors[i])/len(vectors[i]))
        else:
            avg_vector = [0] * vector_dim
        vectorized_comments.append(avg_vector)
    
    if vectorized_comments:  # vectorized_commentsが空でないことを確認
        kmeans = KMeans(n_clusters=min(n_clusters, len(vectorized_comments)), n_init=10, verbose=1, random_state=42).fit(vectorized_comments)
    else:
        print("No comments were vectorized.")

    clustered_comments = {label: [] for label in set(kmeans.labels_)}
    labels = kmeans.labels_
    
    clusterd_display = [] # クラスタリングをした結果、表示をするかどうか
    already_labels = []

    for label, comment in zip(kmeans.labels_, comments):
        clustered_comments[label].append(comment)

        # 初登場のラベルなら表示オン、そうでないなら表示オフ
        if (label in already_labels):
           clusterd_display.append(-1)
        else:
            clusterd_display.append(1)
            already_labels.append(label) 

    

    return clusterd_display, labels


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
    
    if ("errorcode" in result):
        newdata = result

    return JsonResponse(newdata, json_dumps_params={'ensure_ascii': False}, safe=False)

# データベースリセット用API
def api_reset(request):
    reset_database()
    return JsonResponse({})

#==========☆YouTubeコメント欄取得関数 ☆==========
MAX_GET_CHAT = 20 #1度の取得最大数
# YouTubeのチャットを取得する関数
def get_chat(video_id, pageToken, api_key):

    print("\nコメント取得完了開始\n")

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

    # 取得したコメントが0なら終了。
    if (response_data["pageInfo"]["totalResults"] == 0):
        return {}
    
    # nextPageTokenを設定
    userobj = User.objects.get(pk=1)
    userobj.nextPageToken = response_data["nextPageToken"]
    userobj.save()

    # APIの応答に 'error' キーが存在する場合、エラーハンドリングを行う
    if 'error' in response_data:
        print("Error from YouTube API:", response_data['error']['message'])
        # 必要に応じて、その他のエラーハンドリング処理を追加
        return {"errorcode":response_data['error']['message']}  # ここでは空のリストを返すことを例としています
    
    # エラーがない場合、通常の処理を続行
    # 取得したデータからコメントの内容のみをリストとして抽出
    comments = [item["snippet"]["displayMessage"] for item in response_data["items"]]

    # 抽出したコメントをクラスタリング
    print("\nコメント取得完了\nクラスタリング開始\n")
    clusterd_display, clusterd_labels = cluster_data(comments, fasttext_model)  
    print("\nクラスタリング終了")
    #print("クラスタリング:",clustered_comments)
    #ここでclustered_commentsを使う
    print("\nアンチコメントか判定開始\n")
    anti_comments, anti_labels, anti_judge_list = run_moderation_api(comments, clusterd_display)
    print("\n判定終了\n")
    #print("アンチ:",anti_comments,anti_labels)


    # クラスタリング結果をデータベースに保存
    input_database(clusterd_labels, anti_judge_list, response_data["items"], clusterd_display)
    return {}


def view_comments(request):
    # データベースからコメントを取得
    comments = Comments.objects.all().order_by("-posted_at")[:50]
    modelist = ["全部のコメントをアンチコメントか判定するモード(低速)", "分類わけの結果をもとに、表示予定のコメントだけ判定するモード(高速)"]
    commentFastMode = User.objects.get(pk=1).commentFastMode

    context = {
        "comments": comments,
        "Fastmode": modelist[commentFastMode]
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
        print("[views.pyのget_chat_id関数からのお知らせ]\n何かしらの問題によりチャットidが取得できませんでした。\nAPIキーの間違いや、動画URLの間違いなどが考えられます\n（ライブ配信でない動画や、ライブ配信のアーカイブのチャット欄は取得できません。\nまた、コメントが不可な生配信もこのエラーが出ます。）\n")
    

    return chat_id

# Moderation APIを実行する関数を定義する

def run_moderation_api(comments, clusterd_display):
    anti_comments = {label: [] for label in comments}
    thresholdList = [0, 0.0002, 0.0001, 0.00002] #未使用、弱、中、強
    threshold = thresholdList[User.objects.get(pk=1).commentFilterLevel]

    label = None
    anti_judge_list = [] #アンチコメントかどうかの判定結果一覧のリスト

    print("clusterd_display:",clusterd_display)

    try:
        for i in range(len(comments)):

            commentFastMode = User.objects.get(pk=1).commentFastMode

            # クラスタリングした結果、表示しないのであればアンチコメントの判定はしない
            if(clusterd_display[i] == -1 and commentFastMode == 1):
                anti_judge_list.append({"result": 0, "violence_score": 0.0})
                continue

            comment = comments[i]


            #print(f"Processing comment: {comment}")
            response = openai.Moderation.create(input=str(comment))
            #print(f"API Response: {response}")

            category_scores = response['results'][0]['category_scores']
            #print(f"Category Scores: {category_scores}")
            violence_score = category_scores.get('hate', 0)

            print(comment[0:5], "...　　判定結果:[", violence_score > threshold, "]", violence_score)

            if violence_score > threshold:
                #anti_comments[label].append({"comment": comment, "is_ant": True})
                #print(f"アンチコメント（クラスタ {label}）: {comment}, Violence Score: {violence_score}")
                anti_judge_list.append({"result": -1, "violence_score": violence_score})
            else:
                #anti_comments[label].append({"comment": comment, "is_ant": False})
                #print(f"アンチコメント以外（クラスタ {label}）: {comment}, Violence Score: {violence_score}")
                anti_judge_list.append({"result": 1, "violence_score": violence_score})
            
            if (commentFastMode == 0):
                time.sleep(2)
            #print("SUCCESS", anti_comments, label)
    except Exception as e:
        print(f"Error in run_moderation_api: {e}")
        print("\n\n＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝\nエラー! アンチコメントの判定中に止まりました。\nOpenAPIの[50リクエスト/秒]制限を超えている可能性が高いです。\n＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝\n\n")

    print(anti_judge_list)
    

    return anti_comments, label, anti_judge_list



# コメントをデータベースに格納する関数
def input_database(clusterd_labels, anti_judge_list, all_comments, clusterd_display):

    cluster_id_addnumber = (int(time.time()) % 1000) * 10000 #この値をクラスタリング結果に足すことで、複数回に渡ってクラスタリングをしてもラベルを被らせないようにするか検討中。簡易的なもので、20分くらいで1順します。

    # 全部のコメントを取り出し、格納
    for i in range(len(all_comments)):
        new_body = all_comments[i]["snippet"]["displayMessage"]
        new_posted_at = datetime.datetime.strptime(all_comments[i]["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%S.%f%z") + datetime.timedelta(hours=9) #日本時間に合わせるため、文字列をdatetime型に変換したのち+9時間
        new_name = all_comments[i]["authorDetails"]["displayName"]
        new_userid = all_comments[i]["authorDetails"]["channelId"]
        new_cluster_label = clusterd_labels[i]
        new_cluster_display = clusterd_display[i] # 初めてのラベルなら表示ON、そうでないなら表示OFF(表示判定は、クラスタリングを行う関数で行うようにしました)
        new_anti_violence_score = anti_judge_list[i]["violence_score"]
        new_anti_display = anti_judge_list[i]["result"] #アンチジャナイコメントは表示OK(1)、アンチコメントは表示NG(-1)、未判定のものも表示しな(0)。

        comment = Comments(body = new_body, posted_at = new_posted_at, name = new_name, userid = new_userid, cluster_label = new_cluster_label, cluster_display = new_cluster_display, anti_violence_score = new_anti_violence_score, anti_display = new_anti_display)
        comment.save()
    return



# 取得したコメントをリセット。全部消す関数。
def reset_database():
    try:
        userobj = User.objects.get(pk=1)
        userobj.nextPageToken = "0"
        userobj.save()
    except:
        userobj = User(nextPageToken = "0")
        userobj.save()

    for comment in Comments.objects.all():
        comment.delete()
        
    return


#==========☆コメントデータベースからコメントを抜粋する関数 ☆==========
def choose_comment():
    return Comments.objects.all().filter(cluster_display=1, anti_display=1).order_by("-posted_at")[:50] #表示ONなものだけ新着順で抽出。filterのカッコ内にカンマ区切りで条件付け加え可能。
