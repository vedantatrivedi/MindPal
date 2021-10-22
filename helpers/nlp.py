from ibm_watson import ToneAnalyzerV3
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, SyntaxOptions
from ibm_watson.natural_language_understanding_v1 import Features, SyntaxOptions, SyntaxOptionsTokens
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions,SentimentOptions
import requests
import json
import html2text

def analyze_tone(text):
    authenticator = IAMAuthenticator('4Ix2KP-hhcK0RBVkporAYcACkyqX1EyiHofi2cnWpOqn')
    tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
    )
    tone_analyzer.set_service_url('https://api.kr-seo.tone-analyzer.watson.cloud.ibm.com/instances/4114e677-d73f-47ff-8583-7661da80358a')
    # tone_analyzer.set_disable_ssl_verification(True)
    text = html2text.html2text(text) 
    try:
        tone_analysis = tone_analyzer.tone({'text': text}, content_type='application/json').get_result()
        return tone_analysis
    except:
        return 50
    print(type(tone_analysis))
    print(tone_analysis)
    print(tone_analysis['document_tone']['tones'][0]['score'])
    for i in tone_analysis["document_tone"]['tones']:
        for j in range (0,len(i)):
            print(i[j]['score']) 
    
def get_sentiment(journal_text):
    journal_text = html2text.html2text(journal_text) 
    authenticator = IAMAuthenticator('A7kV_7i5nEABd17D-adfvFKhEuF0I0G2tfbsSQY-Fnin')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url('https://api.kr-seo.natural-language-understanding.watson.cloud.ibm.com/instances/6c21b731-5a0f-44d2-854f-906c346c2207') 
    try:
        json_response = (natural_language_understanding.analyze
                         (text=journal_text,features=Features(keywords=
                        KeywordsOptions(sentiment= True,emotion= True,limit= 3),
                        sentiment=SentimentOptions())).get_result())
        score = json_response['sentiment']['document']['score']
        return score*100
    except:
        return 0
    

def get_score(text):
    json_output = analyze_tone(text)
    try:
        total_score = json_output['document_tone']['tones'][0]['score']
    except:
        total_score = 0.5
    return total_score*100


# authenticator = IAMAuthenticator('A7kV_7i5nEABd17D-adfvFKhEuF0I0G2tfbsSQY-Fnin')
# natural_language_understanding = NaturalLanguageUnderstandingV1(
#     version='2021-08-01',
#     authenticator=authenticator
# )

# natural_language_understanding.set_service_url('https://api.kr-seo.natural-language-understanding.watson.cloud.ibm.com/instances/6c21b731-5a0f-44d2-854f-906c346c2207')
# st = "Happiness is a feeling of pleasure and positivity. When someone feels good, proud, excited, relieved or satisfied about something, that person is said to be happy.... Happiness sometimes causes people to cry when they laugh because the emotion takes control of them, people should learn how to be happy in life"
# string = "I am car in Lucknow"

# json_file = (natural_language_understanding.analyze(text=string,features=Features(keywords=KeywordsOptions(sentiment= True,emotion= True,limit= 3),sentiment=SentimentOptions())).get_result())
# print(json_file)
# print(json_file['sentiment']['document']['score'])
# print(json_file['sentiment']['document']['label'])
