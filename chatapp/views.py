from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from chatapp.models import Comments, User
import requests, json


#==========☆ トップページ用関数 ☆==========
def index(request):
    return render(request, "chatapp/index.html")




#==========☆　YouTubeコメント欄取得動作テストページ用関数 ☆==========
# 動作確認用に一時的に作ったページです。
def getchattest(request):
    return render(request, "chatapp/getchattest.html")

# コメント取得をテストページで使えるようにAPI化したもの
def api_getchat(request):

    nextPageToken = User.objects.get(pk=1).nextPageToken
    if (nextPageToken == "0"):
        nextPageToken = None

    video_id = request.GET["youtubeurl"]
    YT_API_KEY = request.GET["apikey"]

    # コメント取得、データベースに保存
    get_chat(video_id, nextPageToken, YT_API_KEY)

    # DBからコメント抽出
    newdata = list(choose_comment().values())


    return JsonResponse(newdata, json_dumps_params={'ensure_ascii': False}, safe=False)

# データベースリセット用API
def api_reset(request):
    reset_database()
    return JsonResponse({})




#==========☆　YouTubeコメント欄取得関数 ☆==========
MAX_GET_CHAT = 10 #1度の取得最大数

# チャットを取得しデータベースに保存させる関数
def get_chat(video_id, pageToken, YT_API_KEY):
    chat_id  = get_chat_id(video_id, YT_API_KEY)
    url    = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
    params = {'key': YT_API_KEY, 'liveChatId': chat_id, 'part': 'id,snippet,authorDetails', 'maxResults':MAX_GET_CHAT}
    if type(pageToken) == str:
        params['pageToken'] = pageToken

    data   = requests.get(url, params=params).json()
    input_database(data)

    return




# ChatのIDを取得する関数(チャットを取得する関数本体で使用)
def get_chat_id(video_id, YT_API_KEY):

    url    = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YT_API_KEY, 'id': video_id, 'part': 'liveStreamingDetails'}
    data   = requests.get(url, params=params).json()

    liveStreamingDetails = data['items'][0]['liveStreamingDetails']
    if 'activeLiveChatId' in liveStreamingDetails.keys():
        chat_id = liveStreamingDetails['activeLiveChatId']
    else:
        chat_id = None

    return chat_id


# 取得したコメントをデータベースに格納する関数
def input_database(data):
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

# 取得したコメントをリセット。全部消す関数。
def reset_database():
    for comment in Comments.objects.all():
        comment.delete()

    userobj = User.objects.get(pk=1)
    userobj.nextPageToken = "0"
    userobj.save()

    




#==========☆　コメントデータベースから重要コメントを抜粋する関数 ☆==========
# ひとまず最新コメントを10件抜粋するようにしています。
def choose_comment():
    return Comments.objects.all().order_by("-posted_at")[:10]
