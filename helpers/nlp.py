from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features
from ibm_watson.natural_language_understanding_v1 import KeywordsOptions, SentimentOptions
import json
import html2text

# authenticator = IAMAuthenticator(os.environ["NLP_1"])
authenticator = IAMAuthenticator('A7kV_7i5nEABd17D-adfvFKhEuF0I0G2tfbsSQY-Fnin')
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2021-08-01',
    authenticator=authenticator
)
# natural_language_understanding.set_service_url(os.environ["NLP_2"])
natural_language_understanding.set_service_url('https://api.kr-seo.natural-language-understanding.watson.cloud.ibm.com/instances/6c21b731-5a0f-44d2-854f-906c346c2207') 


def get_emotions(journal_text):
    journal_text = html2text.html2text(journal_text)
    sadness = joy = fear = disgust = anger = 0
    try:
        json_response = natural_language_understanding.analyze(
            text=journal_text,
            features=Features(
                keywords=KeywordsOptions(emotion=True, limit=2))).get_result()

        # print(json_response['keywords'])
        for doc in json_response['keywords']:
            sadness = doc['emotion']['sadness']
            joy = doc['emotion']['joy']
            fear = doc['emotion']['fear']
            disgust = doc['emotion']['disgust']
            anger = doc['emotion']['anger']

        return_data = {"sadness": sadness, "joy": joy,
                       "fear": fear, "disgust": disgust, "anger": anger}
        return (json.dumps(return_data, indent=2))
    except:
        return_data = {"sadness": 0, "joy": 0,
                       "fear": 0, "disgust": 0, "anger": 0}
        return (json.dumps(return_data, indent=2))


def get_sentiment(journal_text):
    journal_text = html2text.html2text(journal_text)

    try:
        json_response = (natural_language_understanding.analyze
                         (text=journal_text, features=Features(keywords=KeywordsOptions(sentiment=True, emotion=True, limit=3),
                                                               sentiment=SentimentOptions())).get_result())
        score = json_response['sentiment']['document']['score']
        return score*100
    except:
        return 0
