
from googleapiclient.discovery import build
import re
from janome.tokenizer import Tokenizer
from gensim.models import Word2Vec
def get_comments(youtube_video_id, api_key, max_results=100):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=youtube_video_id,
        maxResults=max_results,
        order="time"
    )
    response = request.execute()
    comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
    return comments
# 例の呼び出し方法
api_key = "AIzaSyDpJkQseYjIeAA_9j2vUzY0qxK_c5ZvwoU"
video_ids = ["ZY4WCa06Big", "VZMkIPQBsOg", "mnFW_UacNsA", "yt3BOIXLdyg", "35uE9gESYVc", "jr65N2cRQmQ", "KMm40IETZzU"]  # ここに動画IDを追加
all_comments = []
for video_id in video_ids:
    comments = get_comments(video_id, api_key)
    all_comments.extend(comments)
comments = get_comments(video_id, api_key)
print(comments)
t = Tokenizer()
def preprocess_text(text):
    # 正規化
    text = text.lower()
    text = re.sub(r'\d+', '0', text)  # 数字を0に置き換え
    # 不要な文字の削除
    text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', text)  # URL削除
    text = re.sub(r'[\n\r\t]', ' ', text)  # 改行やタブをスペースに変換
    # 形態素解析
    tokens = t.tokenize(text, wakati=True)
    
    # ストップワードの除去
    stopwords = ["と", "も", "は", "の", "に", "を"]
    tokens = [word for word in tokens if word not in stopwords]
    
    return tokens
# 使用例
text = "YouTubeのURLはhttps://www.youtube.com/ です。"
preprocessed_text = preprocess_text(text)
print(preprocessed_text)  # "youtube url です 。"
preprocessed_comments = [preprocess_text(comment) for comment in all_comments]
# コメントのリストを入力として、モデルを学習
model = Word2Vec(preprocessed_comments, vector_size=100, window=5, min_count=1, workers=4)
model.save("youtube_comments_model.model")
