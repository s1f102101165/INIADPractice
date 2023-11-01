import openai

openai.api_key = "chHJM8Hh_9xSdUvtIKDyWgT9x8BOubw8AMXdvSyUBBEG4YzQMKtUI0Xi6x8Gx1N8Rcoamjl9tNxxmgY79Jaxwwg"
openai.api_base = "https://api.openai.iniad.org/api/v1"

# モデレーションAPIを使用してコメントをモデレート
moderation_resp = openai.Moderation.create(
    input="キモい"
)

# モデレーションAPIのレスポンスから `category_scores` を取得
category_scores = moderation_resp['results'][0]['category_scores']

# category_scoresの中身を確認
print(category_scores)

# 特定のカテゴリのスコアを使用する
"""violence_score = category_scores['violence']
if violence_score > 0.5:
    print("このコメントは暴力的です。")
else:
    print("このコメントは暴力的ではありません。")"""
