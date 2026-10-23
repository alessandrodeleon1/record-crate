from django.shortcuts import render
from django.urls import reverse


# Create your views here.
def index(request):
    return render(request, "home.html")

def listings(request):
    return render(request, "listings.html")
