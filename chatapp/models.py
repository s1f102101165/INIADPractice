
from django.db import models
# Create your models here.

# コメントを格納するデータベース
class Comments(models.Model):
    body = models.TextField() #本文
    name = models.TextField() #コメント投稿者名
    userid = models.TextField() #コメント投稿者のID
    posted_at = models.DateTimeField() #コメント投稿日時（日本時間に合わせるには+9時間）
    cluster_label = models.IntegerField(default=-1) #クラスター番号。おそらく表示したり使ったりはしないけど一応保存しとく
    cluster_display = models.BooleanField(default=False) #クラスタリングした結果、表示するならTrueに（0~3の各分類からそれぞれの代表コメントを1つずつ選んでtrueにする）
    anti_violence_score = models.FloatField(default=0.0) #アンチコメントかどうかの値
    anti_display = models.BooleanField(default=False) #アンチコメントかどうかTrueFalse
    
    def __str__(self):
        return self.body

# 本アプリ使用者(配信者)に関するデータベース
class User(models.Model):
    nextPageToken = models.TextField() #どこまでコメントを読み込んだかを一時保存するトークン
