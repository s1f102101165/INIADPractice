let now_motion = false;


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
        clearInterval(intervalId)
        
        if (json["errorcode"] == "The request is missing a valid API key."){alert("[エラー]\nAPIキーが正しくないです！\nviews.pyを確認してください！")}
        else if (json["errorcode"] == "No filter selected. Expected one of: liveChatId"){alert("[エラー]\nライブ配信のURLが正しくないです！\nスペルミスやコピペミスがないかご確認ください。\n（通常の動画や、ライブ配信のアーカイブなどでは動作しません）")}
        else {alert("[エラー]\n何かしらのエラーによりコメントが取得できませんでした")}
        now_motion = false;
        change_start_butoon()
    }else{
        // エラーなく正常に動作した場合の処理
        n = json.length;
        for(let i=0; i< n; i++){
            clustered_comment = json[i]["body"];
            chatlist = document.getElementById("comment_" + (i));
            chatlist.textContent = clustered_comment;

            clustered_comment = json[i]["name"];
            chatlist = document.getElementById("commentTitle_" + (i));
            chatlist.textContent = clustered_comment;
        }
    }
}

// エンターキーを検知し、チャット取得関数起動
window.document.onkeydown = function(event){
    if( event.key === 'Enter' ){
        getchatapi();
    }
};


// ボタンがクリックされたときに呼び出され、チャットの取得を開始する関数
function getchatapi(){
    if (!now_motion){
        now_motion = true;
        change_start_butoon()


        clearInterval(intervalId)
        delete_comment()

        let youtubeurl = document.getElementById("youtubeurl").value;
        youtubeurl = youtubeurl.replace("https://www.youtube.com/watch?v=", "")


        // 埋め込み動画書き換え
        let youtubeMovieEmbedded = document.getElementById('youtubeMovieEmbedded');
        let newYoutubeUrl = 'https://www.youtube.com/embed/' + youtubeurl + "?autoplay=1&mute=1";
        youtubeMovieEmbedded.setAttribute('src', newYoutubeUrl);

        
        // 動画のタイトル取得(取得出来たらcallback_settitle関数実行して表示)
        fetch ("/api/getmovieapi/?youtubeurl=" + youtubeurl)
        .then(response => response.json())
        .then(callback_movie)
        .catch(error =>{
            console.log("[エラー]:何らかの理由でタイトル取得できてないです")
        })


        reset_api()
        use_getchatapi(youtubeurl);
        intervalId = setInterval(() => getChatLoop(youtubeurl), 10000);
    }
}

// スタートボタンの表示チェンジ
function change_start_butoon(){
    if (now_motion){
        // ボタン　押せなくする
        document.getElementById("startbutton").disabled = "disabled";
    }else{
        // ボタン　通常に
        document.getElementById("startbutton").disabled = false;
        document.getElementById("startbutton").style.opacity = "1.0";
        document.getElementById("startbutton").style.pointer.events= "none";
    }
}



// 動画のタイトル取得したらHTMLをタイトルに書き換え
function callback_movie(json){
    element = document.getElementById("video-title").textContent = json["items"][0]["snippet"]["title"]
}


function delete_comment(){
    for(let i=0; i< 10; i++){
        //chatlist = document.getElementById("comment_" + (i).td);
        //chatlist.textContent = "";
    }
}


// ボタンがクリックされたときに呼び出され、チャットの取得を停止する関数
function getchatstopapi(){
    clearInterval(intervalId)

    // ボタン有効に
    now_motion = false;
    change_start_butoon()
}

// 一定間隔でチャットを取得する関数
function getChatLoop(youtubeurl){
    use_getchatapi(youtubeurl);
}























// debounce関数
function debounce(func, wait) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            func.apply(context, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}


//ハンバーガーメニューをクリックした際の処理
$(function() {
	$('#menubar_hdr').click(function() {
		$(this).toggleClass('ham');

			if($(this).hasClass('ham')) {
				$('#menubar').addClass('d-b');
			} else {
				$('#menubar').removeClass('d-b');
			}

	});
});


// 同一ページへのリンクの場合に開閉メニューを閉じる処理
$(function() {
	$('#menubar a[href^="#"]').click(function() {
		$('#menubar').removeClass('d-b');
		$('#menubar_hdr').removeClass('ham');
	});
});


// スムーススクロール（※通常）
$(window).on("load resize", debounce(function() {
	var hash = location.hash;
	if(hash) {
		$('body,html').scrollTop(0);
		setTimeout(function() {
			var target = $(hash);
			var scroll = target.offset().top;
			$('body,html').animate({scrollTop:scroll},500);
		}, 5);
	}
	$('a[href^="#"]').click(function() {
		var href = $(this).attr('href');
		var target = href == '#' ? 0 : $(href).offset().top;
		$('body,html').animate({scrollTop:target},500);
		return false;
	});
}, 5));


//pagetop
$(function() {
    var scroll = $('.pagetop');
    var scrollShow = $('.pagetop-show');
        $(scroll).hide();
        $(window).scroll(function() {
            if($(this).scrollTop() >= 300) {
                $(scroll).fadeIn().addClass(scrollShow);
            } else {
                $(scroll).fadeOut().removeClass(scrollShow);
            }
        });
});


// 汎用開閉処理
$(function() {
	$('.openclose').next().hide();
	$('.openclose').click(function() {
		$(this).next().slideToggle();
		$('.openclose').not(this).next().slideUp();
	});
});


// 詳細ページのサムネイル切り替え
$(function() {
    // 初期表示: 各 .photo に対して、直後の .thumbnail の最初の画像を表示
    $(".photo").each(function() {
        var firstThumbnailSrc = $(this).next(".thumbnail").find("img:first").attr("src");
        var defaultImage = $("<img>").attr("src", firstThumbnailSrc);
        $(this).append(defaultImage);
    });

    // サムネイルがクリックされたときの動作
    $(".thumbnail img").click(function() {
        var imgSrc = $(this).attr("src");
        var newImage = $("<img>").attr("src", imgSrc).hide();

        // このサムネイルの直前の .photo 要素を取得
        var targetPhoto = $(this).parent(".thumbnail").prev(".photo");

        targetPhoto.find("img").fadeOut(400, function() {
            targetPhoto.empty().append(newImage);
            newImage.fadeIn(400);
        });
    });
});
