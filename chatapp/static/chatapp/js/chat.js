
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

    if ("errorcode" in json){
        // エラーがあった場合の処理
        if (json["errorcode"] == "The request is missing a valid API key."){alert("[エラー]\nAPIキーが正しくないです！\nviews.pyを確認してください！")}
        else if (json["errorcode"] == "No filter selected. Expected one of: liveChatId"){alert("[エラー]\nライブ配信のURLが正しくないです！\n（通常の動画や、ライブ配信のアーカイブなどでは動作しません）")}
        else {alert("[エラー]\n何かしらのエラーによりコメントが取得できませんでした")}
    }else{
        // エラーなく正常に動作した場合の処理
        n = json.length;
        for(let i=0; i< n; i++){
            clustered_comment = json[i]["body"];
            chatlist = document.getElementById("comment_" + (i));
            chatlist.textContent = clustered_comment;
        }
    }
}

// ボタンがクリックされたときに呼び出され、チャットの取得を開始する関数
function getchatapi(){
    clearInterval(intervalId)
    delete_comment()

    let youtubeurl = document.getElementById("youtubeurl").value;
    //var regex = "https://www.youtube.com/watch?v="; //正規表現生成


    
    youtubeurl = youtubeurl.replace("https://www.youtube.com/watch?v=", "")

    
    // 動画のタイトル取得(取得出来たらcallback_settitle関数実行して表示)
    fetch ("/api/getmovieapi/?youtubeurl=" + youtubeurl)
    .then(response => response.json())
    .then(callback_movie)
    .catch(error =>{
        console.log("[エラー]:何らかの理由でタイトル取得できてないです")
    })


    reset_api()
    intervalId = setInterval(() => getChatLoop(youtubeurl), 10000);
}

// 動画のタイトル取得したらHTMLをタイトルに書き換え
function callback_movie(json){
    element = document.getElementById("video-title").textContent = json["items"][0]["snippet"]["title"]
}


function delete_comment(){
    for(let i=0; i< 10; i++){
        chatlist = document.getElementById("comment_" + (i));
        chatlist.textContent = "";
    }
}


// ボタンがクリックされたときに呼び出され、チャットの取得を停止する関数
function getchatstopapi(){
    clearInterval(intervalId)
}

// 一定間隔でチャットを取得する関数
function getChatLoop(youtubeurl){
    use_getchatapi(youtubeurl);
}
