from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
# from users.models import *
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from Like.models import Main_Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



# def news(request):
#     news = New.objects.all().order_by('-date_updated')
#     popular = New.objects.filter(popular=True).order_by('-date_updated')[0:3]
#     category = Main_Category.objects.all().order_by('-id')
#     if request.method == 'POST':
#         email = request.POST.get('EMAIL')
#         print("this the email",email)
#         Email.objects.create(emais=email)
#     constant = {
#         'news':news,
#         'popular':popular,
#         "category":category,
#     }
#     return render(request,"blog/news.html",constant)


def news(request):
    news_list = New.objects.all().order_by('-date_updated')
    paginator = Paginator(news_list, 2)  # Change '10' to the number of articles per page you want

    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        news = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page of results.
        news = paginator.page(paginator.num_pages)

    popular = New.objects.filter(popular=True).order_by('-date_updated')[0:3]
    category = Main_Category.objects.all().order_by('-id')
    
    if request.method == 'POST':
        email = request.POST.get('EMAIL')
        print("this the email",email)
        Email.objects.create(emais=email)
    
    constant = {
        'news': news,
        'popular': popular,
        "category": category,
    }
    
    return render(request, "blog/news.html", constant)


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