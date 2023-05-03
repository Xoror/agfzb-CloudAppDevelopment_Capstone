import requests
import json
from .models import CarDealer, CarReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


def get_request(url, **kwargs):
    print(kwargs)
    print("Get from {}".format(url))
    api_key = kwargs.get("apikey")
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, auth=HTTPBasicAuth('apikey', api_key), headers={'Content-Type': 'application/json'})
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


def get_dealers_from_cf(url, **kwargs):#, id="", state="", **kwargs):
    results = []
    test_id = kwargs.get("id")
    test_state = kwargs.get("state")
    if(test_id != None):
        json_result = get_request(url, id=test_id)
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
            results.append(dealer_obj)
        print(counter)
    return results

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url, dealership=dealer_id)
    if json_result:
        reviews = json_result["rows"]
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
            #review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
    return results



def analyze_review_sentiments(dealer_review):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    apikey = "ZWeOsOsnjedSWilr6FnZIXgeq_O_bmBQ4oupwsP4Sjql"
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com"
    
    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=dealer_review,
        language='en',
        features=Features(sentiment=SentimentOptions(targets=[dealer_review]))
    ).get_result()

    print(json.dumps(response, indent=2))
    
    return response["sentiment"]["document"]["label"]



