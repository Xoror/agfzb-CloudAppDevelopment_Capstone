import requests
import json
from .models import CarDealer, CarReview
from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, ClassificationsOptions


def get_request(url, **kwargs):
    print(kwargs)
    print("Get from {}".format(url))
    api_key = kwargs.get("apikey")
    try:
        if api_key:
            response = requests.post(url, auth={'apikey':api_key}, json={"IAM_API_KEY":"ZWeOsOsnjedSWilr6FnZIXgeq_O_bmBQ4oupwsP4Sjql"}, headers={'Content-Type': 'application/json'})
        else:
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'})
    except:
        print("Network exception occured")
    status_code = response.status_code
    print("With status {}".format(status_code))
    #print(response.text)
    json_data = json.loads(response.text)
    return json_data
#


def post_request(url, review, **kwargs):
    payload = {}
    payload["review"] = review
    print("Post to {}".format(url))
    try:
        response = requests.post(url, json=payload)
    except:
        print("Network exception occured")
    status_code = response.status_code
    print("With status {}".format(status_code))

def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None
def get_dealers_from_cf(url, **kwargs):#, id="", state="", **kwargs):
    results = []
    states = []
    test_id = kwargs.get("id")
    test_state = kwargs.get("state")
    if(test_id != None):
        json_result = get_request(url, id = test_id)
    elif (test_state != None):
        json_result = get_request(url, state=test_state)
    else:
        json_result = get_request(url)
    
    if json_result:
        dealers = json_result["rows"]
        counter=0
        for dealer in dealers:
            counter +=1
            if(test_id != None or test_state != None):
                dealer_doc = dealer
            else:
                dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(
                id=dealer_doc["id"], 
                city=dealer_doc["city"], 
                state=dealer_doc["state"], 
                st=dealer_doc["st"], 
                address=dealer_doc["address"], 
                zip=dealer_doc["zip"], 
                lat=dealer_doc["lat"], 
                long=dealer_doc["long"], 
                short_name=dealer_doc["short_name"],
                full_name=dealer_doc["full_name"]
            )
            test = find_element_in_list(dealer_doc["state"], states)
            if(test == None):
                states.append(dealer_doc["state"])
            results.append(dealer_obj)
        print(counter)
        states.sort()
    return [results, states]

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url, dealershipID=str(dealer_id))
    if json_result:
        reviews = json_result["docs"]
        for review in reviews: 
            review_obj = CarReview(
                id=review["id"],
                name=review["name"],
                dealership=review["dealership"],
                review=review["review"],
                purchase=review["purchase"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment = "neutral"
            )
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
    return results



def analyze_review_sentiments(dealer_review):
    apikey = "qXhcylrnsRepZcSwClUN4ttwXfOZSGCKwrCdT4rG-7tt"
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/be48975c-a6be-4e7c-8c69-59f9813123ca"
    
    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-08-10',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=dealer_review,
        features=Features(classifications=ClassificationsOptions(model="2303094c-0943-4974-9052-cd79b8c6bb6d")),
    )
    #print(response.result["classifications"][0]["class_name"])
    return response.result["classifications"][0]["class_name"]



