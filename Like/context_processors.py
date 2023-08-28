from django.shortcuts import render

def add_request_to_context(request):
    return {'request': request}


