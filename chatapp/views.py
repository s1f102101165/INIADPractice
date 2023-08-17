from django.shortcuts import render
from django.http import JsonResponse
import requests


#==========☆ トップページ用関数 ☆==========
def index(request):
    return render(request, "chatapp/index.html")




#==========☆　YouTubeコメント欄取得動作テストページ用関数 ☆==========
# 動作確認用に一時的に作ったページです。
def getchattest(request):
    return render(request, "chatapp/getchattest.html")

# テストページで使えるようにAPI化したもの
def api_getchat(request):#, yt_url, nextPageToken
    nextPageToken = None
    video_id = request.GET["youtubeurl"]
    YT_API_KEY = request.GET["apikey"]


    data = get_chat(video_id, nextPageToken, YT_API_KEY)

    return JsonResponse(data)





#==========☆　YouTubeコメント欄取得関数 ☆==========

# チャットを取得する関数本体
def get_chat(video_id, pageToken, YT_API_KEY):
    chat_id  = get_chat_id(video_id, YT_API_KEY)
    url    = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
    params = {'key': YT_API_KEY, 'liveChatId': chat_id, 'part': 'id,snippet,authorDetails'}
    if type(pageToken) == str:
        params['pageToken'] = pageToken

    data   = requests.get(url, params=params).json()

    return data




# ChatのIDを取得する関数(チャットを取得する関数本体で使用)
def get_chat_id(video_id, YT_API_KEY):

    url    = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YT_API_KEY, 'id': video_id, 'part': 'liveStreamingDetails'}
    data   = requests.get(url, params=params).json()

    liveStreamingDetails = data['items'][0]['liveStreamingDetails']
    if 'activeLiveChatId' in liveStreamingDetails.keys():
        chat_id = liveStreamingDetails['activeLiveChatId']
        print('get_chat_id done!')
    else:
        chat_id = None
        print('NOT live')

    return chat_id