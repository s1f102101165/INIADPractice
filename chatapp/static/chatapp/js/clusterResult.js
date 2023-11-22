
// ボタンがクリックされたときに呼び出され、チャットの取得を開始する関数
function getchatapi(){
    let apikey = document.getElementById("apikey").value;
    let youtubeurl = document.getElementById("youtubeurl").value;
    window.location.href = 'clusterResultJSON?apikey=' + apikey + "&youtubeurl=" + youtubeurl;
}