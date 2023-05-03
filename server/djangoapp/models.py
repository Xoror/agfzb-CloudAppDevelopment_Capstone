from django.db import models
from django.utils.timezone import now

class CarMake(models.Model):
    name = models.CharField(max_length=100, default="Audi")
    description = models.CharField(max_length=400, default="Default description")

    def __str__(self):
        return "Name: " + self.name + ", " + \
                "Description: " + self.description

class CarModel(models.Model):
    carMake = models.ForeignKey(CarMake, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, default="A6")
    dealer_id = models.IntegerField(default=1)
    year = models.DateField(default="01/01/1970")

    options = [("sedan", "Sedan"), ("suv", "SUV"), ("wagon", "WAGON")]
    carType = models.CharField(max_length=100, choices=options, default="sedan")
    test = models.CharField(max_length=10, default="test")

    def __str__(self):
        return "Name: " + self.name + ", " + self.carType

class CarDealer:
    def __init__(self, id, city, state, st, address, zip, lat, long, short_name, full_name):
        self.id = id
        self.city = city
        self.state = state
        self.st = st
        self.address = address
        self.zip = zip
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.full_name = full_name
    def __str__(self):
        return "Dealer name: " + self.full_name


class CarReview:
    def __init__(self, id, name, dealership, review, purchase, purchase_date, car_make, car_model, car_year, sentiment):
        self.id = id
        self.name = name
        self.dealership = dealership
        self.review = review
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment
    def __str__(self):
        return "Review: " + self.review
