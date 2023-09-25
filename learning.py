import pandas as pd
from gensim.models import Word2Vec
import requests
import MeCab

df = pd.read_csv('youtube_comments.csv',header = None)

###前処理開始###

df.columns = ["comment"]
df = df.drop(0)
df = df.reset_index(drop=True)
df = df.dropna(subset=['comment'])
#print(df.head())

#絵文字を取り除く
#英語を取り除く
df['comment'] = df['comment'].str.replace('<br>', '', regex=True)\
                             .str.replace(r'[\U00010000-\U0010ffff]', '', regex=True)\
                             .str.replace(r'[a-zA-Z]', '', regex=True)

###前処理終了###

def get_stop_words():
    url = "http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt"
    r = requests.get(url)
    tmp = r.text.split('\r\n')
    stop_words = []
    for i in range(len(tmp)):
        if len(tmp[i]) < 1:
            continue
        stop_words.append(tmp[i])
    stop_words = stop_words + ['が', 'で', 'は', 'の', 'も', 'を', 'て', 'に', 'だ', 
                               'と', 'た', 'や', 'ます', 'など', 'あり', 'する', 'ある', 
                               'な', 'き', 'いる', 'から', 'そう', 'し', 'おり', 'ば', 'なら',
                               'いう', 'れ', 'かつ', 'か', 'ない', 'です']
    return stop_words

stop_words = get_stop_words()

def parse_comment(comment, tagger=None, stop_words=None):
    try:
        lines = tagger.parse(comment).split('\n')
    except TypeError:
        print(comment)
    except AttributeError:
        print(comment)
        
    word_list = []
    for line in lines:
        if line == 'EOS':
            break
        if line in stop_words:
            continue
        word = line.split('\t')[0]
        word_list.append(word)
    return ' '.join(word_list)


tagger = MeCab.Tagger("-Owakati")

# 各コメントを分かち書きしてリストに保存
wakati_list = [parse_comment(comment, tagger=tagger, stop_words=stop_words).split() for comment in df['comment']]
df['wakati'] = [' '.join(words) for words in wakati_list]

# コメントのリストを入力として、モデルを学習
model = Word2Vec(wakati_list, vector_size=100, window=5, min_count=1, workers=4)
model.save("youtube_comments_model.model")