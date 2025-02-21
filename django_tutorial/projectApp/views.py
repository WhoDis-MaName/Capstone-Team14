from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
 
 
def index(request):
  return HttpResponse("Here is the index")
 
# Defining a function which
# will receive request and
# perform task depending 
# upon function definition
def hello_geeks (request) :
 
    # This will return Hello Geeks
    # string as HttpResponse
    return HttpResponse("Hello Geeks")