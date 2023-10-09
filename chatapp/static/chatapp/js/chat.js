
// タイマーIDを保存する変数の定義
let intervalId;
// views.pyのAPIを呼び出して、既存のコメントデータベースをリセットする関数
function reset_api(){
    apiurl = "/api/resetapi/";
    fetch(apiurl)
}

// views.pyのAPIを呼び出して、チャットデータを取得する関数
function use_getchatapi(youtubeurl){
    apiurl = "/api/getchatapi/?youtubeurl=" + youtubeurl;
    fetch(apiurl)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok'); 
        }
        return response.json();
    })
    .then(callback)
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error.message);
    });
}

// use_getchatapi関数がJSONを正常に取得した場合に呼び出されるコールバック関数
function callback(json){
    console.log(json);
    n = json.length;
    for(let i=0; i< n; i++){
        clustered_comment = json[i]["body"];
        chatlist = document.getElementById("comment_" + (i));
        chatlist.textContent = clustered_comment;
    }
}

// ボタンがクリックされたときに呼び出され、チャットの取得を開始する関数
function getchatapi(){

    let youtubeurl = document.getElementById("youtubeurl").value;
    var regex = "https://www.youtube.com/watch?v="; //正規表現生成


    youtubeurl = youtubeurl.replace("https://www.youtube.com/watch?v=", "")
    
    // 動画のタイトル取得(取得出来たらcallback_settitle関数実行)
    fetch ("/api/getmovieapi/?youtubeurl=" + youtubeurl)
    .then(response => response.json())
    .then(callback_movie)


    reset_api()
    intervalId = setInterval(() => getChatLoop(youtubeurl), 10000);
}

// 動画のタイトル取得したらHTMLをタイトルに書き換え
function callback_movie(json){
    element = document.getElementById("video-title").textContent = json["items"][0]["snippet"]["title"]
}



// ボタンがクリックされたときに呼び出され、チャットの取得を停止する関数
function getchatstopapi(){
    clearInterval(intervalId)
}

// 一定間隔でチャットを取得する関数
function getChatLoop(youtubeurl){
    use_getchatapi(youtubeurl);
}
