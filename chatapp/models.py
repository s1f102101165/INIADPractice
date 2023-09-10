
from django.db import models
# Create your models here.

# コメントを格納するデータベース
class Comments(models.Model):
    body = models.TextField() #本文
    name = models.TextField() #コメント投稿者名
    userid = models.TextField() #コメント投稿者のID
    posted_at = models.DateTimeField() #コメント投稿日時（日本時間に合わせるには+9時間）
    def __str__(self):
        return self.body

# 本アプリ使用者(配信者)に関するデータベース
class User(models.Model):
    nextPageToken = models.TextField() #どこまでコメントを読み込んだかを一時保存するトークン
