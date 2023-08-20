let intervalId



// views.pyのAPI呼び出し
function resete_api(){
    apiurl = "/api/resetapi/"
    

    fetch(apiurl)
}


// views.pyのAPI呼び出し
function use_getchatapi(apikey, youtubeurl){
    apiurl = "/api/getchatapi/?apikey=" + apikey +"&youtubeurl=" + youtubeurl

    fetch(apiurl)
    .then(response => response.json())
    .then(callback)
}




// use_getchatapiでJSONが取得できたら実行
function callback(json){
    console.log(json)


    // 取得できたコメント数取得
    n = json.length

    
    // コメントを表示していく
    for(let i=0; i< n; i++){
        // JSONから必要なもの抽出
        username = json[i]["name"]
        text = json[i]["body"]
        
        // li要素変更
        chatlist = document.getElementById("comment_" + (9-i))
        chatlist.textContent = username + "：" + text
    }
}


// ボタンが押されたら無限ループ着火
function getchatapi(){
    apikey = document.getElementById("apikey").value;
    youtubeurl = document.getElementById("youtubeurl").value;

    // コメントDBリセット
    resete_api()

    intervalId = setInterval(getChatLoop, 2000)
}

// ボタンが押されたら無限ループストップ
function getchatstopapi(){
    clearInterval(intervalId)
}



// 無限にチャットを取得するループ
function getChatLoop(){
    use_getchatapi(apikey, youtubeurl, 0)
}