from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
# from users.models import *
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum



def news(request):
    news = New.objects.all().order_by('-date_updated')
    popular = New.objects.filter(popular=True).order_by('-date_updated')[0:3]
    if request.method == 'POST':
        email = request.POST.get('EMAIL')
        print("this the email",email)
        Email.objects.create(emais=email)
    constant = {
        'news':news,
        'popular':popular
    }
    return render(request,"blog/news.html",constant)




def news_detail(request, id):
    news = get_object_or_404(New, id=id)
    popular = New.objects.filter(popular=True).order_by('-date_updated')[0:3]
    news1 = New.objects.filter(approved=True)[0:1]
    news2 = New.objects.filter(approved=True)[2:4]
    if request.method == 'POST':
        email = request.POST.get('EMAIL')
        print("this the email",email)
        Email.objects.create(emais=email)
    context = {
        "news1":news1,
        "news2":news2,
        "news":news,
        'popular':popular,
    }
    return render(request, 'blog/post-single.html',context)