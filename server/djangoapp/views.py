from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarReview, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/about.html", context)


def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/contact.html", context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, "djangoapp/login.html", context)
    else:
        return render(request, "djangoapp/login.html", context)


def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')


def registration_request(request):
    context = {}
    if (request.method == "GET"):
        return render(request, "djangoapp/registration.html", context)
    if (request.method =="POST"):
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New User")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context["message"] = "User already exists or username is taken."
            return render(request, "djangoapp/registration.html", context)


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/334d0dd7-f8d4-4bbf-a8b9-763e83ba4a2d/dealership-package/get-dealership"
        #url = "https://eu-de.functions.cloud.ibm.com/api/v1/namespaces/334d0dd7-f8d4-4bbf-a8b9-763e83ba4a2d/actions/dealership-package/get-dealership?blocking=true" 
        #apikey = "ZWeOsOsnjedSWilr6FnZIXgeq_O_bmBQ4oupwsP4Sjql"
        dealerships = get_dealers_from_cf(url)#, apikey=apikey)
        context["dealerships"] = dealerships[0]
        context["states"] = dealerships[1]
        return render(request, "djangoapp/index.html", context)
        # return HttpResponse(dealer_names)


def get_dealer_details(request, dealer_id):
    context = {}
    if request.method =="GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/334d0dd7-f8d4-4bbf-a8b9-763e83ba4a2d/dealership-package/get_review_py"
        reviews = get_dealer_reviews_from_cf(url, dealer_id = dealer_id)
        url2 = url = "https://eu-de.functions.appdomain.cloud/api/v1/web/334d0dd7-f8d4-4bbf-a8b9-763e83ba4a2d/dealership-package/get-dealership"
        dealership = get_dealers_from_cf(url2, id= dealer_id)
        print(dealership)
        context["reviews"] = reviews
        context["dealership"] = dealership[0][0]
        return render(request, "djangoapp/dealer_details.html", context)

def add_review(request, dealer_id):
    context = {}
    url = "https://eu-de.functions.appdomain.cloud/api/v1/web/334d0dd7-f8d4-4bbf-a8b9-763e83ba4a2d/dealership-package/get-dealership"
    dealership = get_dealers_from_cf(url, id=dealer_id)
    context["dealership"] = dealership[0][0]
    if request.method == "GET":
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, "djangoapp/add_review.html", context)
    if request.method == "POST":
        if request.user.is_authenticated:
            review = {}
            
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            review["name"] = request.user.username
            review["dealership"] = dealer_id
            review["id"] = dealer_id
            review["purchase"] = False
            if request.POST["purchase"]:
                if request.POST["purchase"] == "on":
                    review["purchase"] = True
            review["purchase_date"] = request.POST["date"]
            review["car_make"] = car.carMake.name
            review["car_model"] = car.name
            review["car_year"] = int(car.year.strftime("%Y"))
            review["review"] = request.POST["review"]
            review["sentiment"] = "neutral"

            url = "https://eu-de.functions.appdomain.cloud/api/v1/web/334d0dd7-f8d4-4bbf-a8b9-763e83ba4a2d/dealership-package/post-review"
            post_request(url, review=review)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

