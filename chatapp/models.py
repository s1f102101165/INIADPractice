
from django.db import models
# Create your models here.

# コメントを格納するデータベース
class Comments(models.Model):
    body = models.TextField() #コメント本文
    name = models.TextField() #コメント投稿者名
    userid = models.TextField() #コメント投稿者のID
    posted_at = models.DateTimeField() #コメント投稿日時
    cluster_label = models.IntegerField(default=-1) #クラスター番号。アプリ上では表示したり使ったりはしないと思うけれど、一応保存してあります。基本は1~3のいずれかになります。
    cluster_display = models.IntegerField(default=0) #クラスタリングした結果、表示するなら1、しないなら-1。（cluster_labelが0~3の各分類からそれぞれの代表コメントを1つずつ選んで1にする）
    anti_violence_score = models.FloatField(default=0.0) #アンチコメントかどうかの値(小数値)
    anti_display = models.IntegerField(default=0)#アンチコメントか判別した結果、表示してOKかどうか。表示OKなら1、NGなら-1。アンチコメントか未判別なら0。
    
    def __str__(self):
        return self.body

# 本アプリ使用者(配信者)に関するデータベース
class User(models.Model):
    nextPageToken = models.TextField() #どこまでコメントを読み込んだかを一時保存するトークン
    useOpenAIAPI = models.TextField(default="") #オップンAIのAPIを保存する用の項目。開発中に班員さんと同じタイミングでアプリを使った際にバッティングしないようにするために使うかも。開発用の項目で、本番では使わない。
    commentFastMode = models.IntegerField(default=1) #コメント分類機能で振り分けた結果、表示されないコメントのアンチコメント判定をすっ飛ばすかどうか
    commentFilterLevel = models.IntegerField(default=2) #アンチコメントのフィルターレベル 1:弱 2:中 3:強