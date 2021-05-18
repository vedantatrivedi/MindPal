from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
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
    # print(type(tone_analysis))
    # print(tone_analysis)
    # print(tone_analysis['document_tone']['tones'][0]['score'])
    # for i in tone_analysis["document_tone"]['tones']:
    #     for j in range (0,len(i)):
    #         #Append the attributes to the data
    #         print(i[j]['score']) 
    

def get_score(text):
    json_output = analyze_tone(text)
    # json_object = json.load(json_output)
    try:
        total_score = json_output['document_tone']['tones'][0]['score']
    except:
        total_score = 0.5
    # print(total_score)
    return total_score*100
# analyze_tone("Today is the day I free myself") 
