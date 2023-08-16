from django.shortcuts import render


#==========☆ トップページ用関数 ☆==========
def index(request):
    return render(request, "chatapp/index.html")