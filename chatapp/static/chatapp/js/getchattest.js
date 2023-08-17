

function use_getchatapi(apikey, youtubeurl){
    fetch("/api/getchatapi/?apikey=" + apikey +"&youtubeurl=" + youtubeurl)
    .then(response => response.json())
    .then(callback)
}

// use_getchatapiでJSONが取得できたら実行
function callback(json){

    // 取得できたコメント数取得
    n = json["pageInfo"]["totalResults"]

    
    for(let i=0; i< n-1; i++){
        username = json["items"][i]["authorDetails"]["displayName"]
        text = json["items"][i]["snippet"]["textMessageDetails"]["messageText"]

        const newli = document.createElement("li")
        newli.textContent = username + "：" + text
        chatlist = document.getElementById("commentlist")
        chatlist.appendChild(newli)
    }

    console.log(json)

}


// ボタンが押されたら実行。
function getchatapi(){
    apikey = document.getElementById("apikey").value;
    youtubeurl = document.getElementById("youtubeurl").value;

    use_getchatapi(apikey, youtubeurl)
}