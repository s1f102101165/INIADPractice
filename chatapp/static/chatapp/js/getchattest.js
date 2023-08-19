// nexttokenはひとまずグローバル変数で管理。もっと良い方法があれば変えるかも..
let nexttoken = null
let intervalId


// views.pyのAPI呼び出し
function use_getchatapi(apikey, youtubeurl){
    if(nexttoken != null){
        apiurl = "/api/getchatapi/?apikey=" + apikey +"&youtubeurl=" + youtubeurl + "&nexttoken=" + nexttoken
    }else{
        apiurl = "/api/getchatapi/?apikey=" + apikey +"&youtubeurl=" + youtubeurl
    }

    fetch(apiurl)
    .then(response => response.json())
    .then(callback)
}




// use_getchatapiでJSONが取得できたら実行
function callback(json){

    // 新しいコメントが存在したら
    if ("pageInfo" in json){

        // 取得できたコメント数取得
        n = json["pageInfo"]["resultsPerPage"]

        
        // コメントを表示していく
        for(let i=0; i< n-1; i++){
            // JSONから必要なもの抽出
            username = json["items"][i]["authorDetails"]["displayName"]
            text = json["items"][i]["snippet"]["textMessageDetails"]["messageText"]
            
            // li要素追加
            const newli = document.createElement("li")
            newli.textContent = username + "：" + text
            chatlist = document.getElementById("commentlist")
            chatlist.appendChild(newli)
        }

        nexttoken = json["nextPageToken"]
    }
}


// ボタンが押されたら無限ループ着火
function getchatapi(){
    apikey = document.getElementById("apikey").value;
    youtubeurl = document.getElementById("youtubeurl").value;

    intervalId = setInterval(getChatLoop, 2000)
}

// ボタンが押されたら無限ループストップ
function getchatstopapi(){
    clearInterval(intervalId)
}



// 無限にチャットを取得するループ
function getChatLoop(){
    use_getchatapi(apikey, youtubeurl, null)
}