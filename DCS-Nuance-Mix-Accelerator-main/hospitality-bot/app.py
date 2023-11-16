# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:11:14 2023

@author: rramesh025
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""

# Using flask to make an api
# import necessary libraries and functions
import requests
import json
import pyodbc
import datetime
from flask import Flask, jsonify, request
from prompt_template import *
import openai
from communicate import res_id_mail, res_id_sms
  
# creating a Flask app
app = Flask(__name__)

res = 2

client = "Paradise resorts"

headers = {
  'Ocp-Apim-Subscription-Key': 'a804d41345194b1ea518cc6424324d9e',
  'Content-Type': 'application/json'
}

url = "https://nuance-mix-language-api.cognitiveservices.azure.com//language/:analyze-text?api-version=2022-05-01"
query_url= "https://nuance-mix-language-api.cognitiveservices.azure.com//language/:query-text?api-version=2021-10-01"
# qna_url = "https://nuance-mix-language-api.cognitiveservices.azure.com/language/:query-knowledgebases?api-version=2021-10-01&deploymentName=test&projectName=Nuanceqna-project"
qna_url = "https://nuance-mix-language-api.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=Nuanceqna-project&api-version=2021-10-01&deploymentName=production"
openai.api_type = ""
openai.api_base = ""
openai.api_version = "" 
openai.api_key = ""
# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET'])
def home():
    return jsonify({'sentiment': "API for sentiment"})

def openaibot_v2(prompts, responses):
    assert len(prompts) == len(responses) 
    try: 
        keywords = summarize_keywords(prompts, responses).split(':')[1]
        print("QUERY: ",keywords)
        links = bing_links(keywords)
        print(links)
        task = form_chatbot_prompt_v2(prompts, responses, links)
        response = openai.ChatCompletion.create(
                    # engine="davinci003",
                    engine="turbo",
                    messages=task,
                    temperature=0,
                    max_tokens=128,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0)["choices"][0]["message"]["content"]
        code = 0
    except Exception as e:
        response, code = "I'm sorry, I'm having trouble processing your request. Please try again later or contact customer support for assistance.", 1
    return response, code 

def openaibot(prompts, responses):
    assert len(prompts) == len(responses) 
    task = form_chatbot_prompt(prompts, responses)
    print(task)
    try: 
        response = openai.ChatCompletion.create(
                    # engine="davinci003",
                    engine="turbo",
                    messages=task,
                    temperature=0,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0)["choices"][0]["message"]["content"]
        code = 0
    except Exception as e:
        response, code = "I'm sorry, I'm having trouble processing your request. Please try again later or contact customer support for assistance.", 1
    return  response, code
    
@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():
    input_text = request.json["input_text"]
    payload = {"kind": "SentimentAnalysis","parameters": {"modelVersion": "latest"},"analysisInput": {"documents": [{"id": "1","language": "en","text": input_text}]}}
    payload = json.dumps(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    result_data = json.loads(response.text)
    sentiment = result_data["results"]["documents"][0]["sentiment"]
    score = result_data["results"]["documents"][0]["confidenceScores"][sentiment]
    return jsonify({'sentiment': sentiment,"score": score, "returnCode" : "0"})
 
@app.route('/getClient', methods = ['GET'])
def getclient():
    global client
    return jsonify({'client': client, "returnCode" : "0"})



@app.route('/updateClient', methods = ['GET','POST'])
def updateClient():
    global client
    client_name = request.json["client"]
    client = client_name
    return jsonify({'result': "New client has been updated","returnCode" : "0"})

#@app.route('/qna', methods = ['GET','POST'])
#def qna():
#    input_text = request.json["input_text"]
#    payload= {"question":input_text,"records": [{"id": "1","text": "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it."},{"id": "2","text": "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface."}],"language": "en"}
#    payload = json.dumps(payload)
#    response = requests.request("POST", query_url, headers=headers, data=payload)
#    result_data = json.loads(response.text)
#    result_data_1= result_data["answers"][0]["answer"]
#    return jsonify({'answer': result_data_1,"returnCode" : "0"})

#  print(result_data)

@app.route('/makeReservation', methods = ['GET','POST'])
def addReservation():
    global res
    # Trusted Connection to Named Instance
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:chatbot-accelerator.database.windows.net,1433;Database=chatbot_db;Uid=serverAdmin;Pwd=ai2ai2ai@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    user_id = int(request.json["user_id"])
    book_room_type = request.json["book_room_type"]
    res_id = str(int(user_id))+str(res)
    no_rooms = request.json["no_of_rooms"]
    start_date = request.json["startdate"]
    end_date = request.json["enddate"]
    service = request.json["reserve_service"]
    cursor=connection.cursor()
    insert_query = f"insert into [dbo].[nuance_reservation](user_id, res_id, no_rooms, start_date, end_date, service, room_type) values ('{str(user_id)}','{str(res_id)}',{no_rooms},'{start_date}','{end_date}','{service}','{book_room_type}')"
    cursor.execute(insert_query)
    cursor.commit()
    connection.close()
    res = res+1
    return (jsonify({"status":"Reservation has been stored successfully", "reservation_id" : res_id, "returnCode" : "0"}))

@app.route('/makeComplaints', methods = ['GET','POST'])
def addTicket():
    global res
    # Trusted Connection to Named Instance
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:chatbot-accelerator.database.windows.net,1433;Database=chatbot_db;Uid=serverAdmin;Pwd=ai2ai2ai@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    user_id = int(request.json["user_id"])
    description = request.json["description"]
    now = datetime.datetime.now()
    start_date = now.strftime('%Y-%m-%d')
    #end_date = ""
    status = request.json["comp_status"]
    service = request.json["service"]
    cursor=connection.cursor()
    insert_query = f"insert into [dbo].[nuance_tickets](user_id, description, status, start_date,service) values ('{str(user_id)}','{str(description)}','{status}','{start_date}','{service}')"
    cursor.execute(insert_query)
    cursor.commit()
    connection.close()
    return (jsonify({"status":"complaint has been stored successfully", "returnCode" : "0"}))

@app.route('/getComplaints', methods = ['GET',"POST"])
def getTicket():
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:chatbot-accelerator.database.windows.net,1433;Database=chatbot_db;Uid=serverAdmin;Pwd=ai2ai2ai@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    user_id = int(request.json["user_id"])
    query = f"select service from [dbo].[nuance_tickets] where user_id = '{user_id}' and status = 'open' order by start_date desc"
    cursor=connection.cursor()
    cursor.execute(query)
    row = cursor.fetchall()
    if len(row) > 0 :
        service = row[0][0]
    else:
        service = "0"
    connection.close()
    return (jsonify({"service":service, "returnCode" : "0"}))

## check upcoming user resevations

@app.route('/getReservation', methods = ['GET',"POST"])
def getReservation():
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:chatbot-accelerator.database.windows.net,1433;Database=chatbot_db;Uid=serverAdmin;Pwd=ai2ai2ai@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    user_id = int(request.json["user_id"])
    query = f"select service,start_date,res_id from [dbo].[nuance_reservation] where user_id = '{user_id}' and start_date <= GETDATE()+7"
    cursor=connection.cursor()
    cursor.execute(query)
    row = cursor.fetchall()
    if len(row) > 0 :
        service = row[0][0]
        service = service.split(",")
        service = [x.strip() for x in service]
        service = ", ".join(list(set(service)))
        vstartdate = row[0][1].strftime('%Y-%m-%d')
        res_id = row[0][2]
    else :
        service = "0"
        vstartdate ="0"
        res_id = "0"
    connection.close()
    return (jsonify({"service":service,"vstartdate" : vstartdate, "res_id":res_id , "returnCode" : "0"}))

### update service column in the database

@app.route('/updateAddon', methods = ['GET',"POST"])
def updateAddon():
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:chatbot-accelerator.database.windows.net,1433;Database=chatbot_db;Uid=serverAdmin;Pwd=ai2ai2ai@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    #user_id = int(request.json["user_id"])
    res_id = int(request.json["res_id"])
    service = request.json["reservation_services"]
    query = f"update [dbo].[nuance_reservation] set service = CONCAT(COALESCE(service,''), ',','{service}') where res_id = '{res_id}'"
    cursor=connection.cursor()
    cursor.execute(query)
    cursor.commit()
    connection.close()
    return (jsonify({"status":"addon has been updated successfully", "returnCode" : "0"}))
  
    
@app.route('/qna', methods = ['POST'])
def qna():
    # import requests_async as requests
    input_text = request.json["input_text"]
    payload = {"question": input_text,"top": 3, "confidenceScoreThreshold": 0.2,"rankerType": "Default","answerSpanRequest": {"enable": True, "confidenceScoreThreshold": 0, "topAnswersWithSpan": 1}, "includeUnstructuredSources": True}
    payload = json.dumps(payload)
    response = requests.request("POST", qna_url, headers=headers, data=payload)
    result_data = json.loads(response.text)
    answer = result_data['answers'][0]['answer']
    # if result_data['answers'][0].get("answerSpan") : 
    #     short_answer = result_data['answers'][0].get("answerSpan")["text"].strip()
    # else:
    short_answer = "0"
    if answer == "No answer found" or answer == "No good match found in KB":
        # prompts = request.json["user_input_var"].split("####")[:-1]
        # responses = request.json["bot_input_var"].split("####")[:-1]
        # answer, code = openaibot(prompts, responses)
        # answer, code = openaibot_v2(prompts, responses)
        answer = "I apologize, but unfortunately, I don't have access to the information you are requesting."

        short_answer = "0"
    if "?" in answer:
        ask_q = "no"
    else:
        ask_q = "yes"
    return (jsonify({"short_answer":short_answer,"answer":answer, "ask_q":ask_q, "returnCode" : "0"}))
    #return (jsonify({"answer":answer, "returnCode" : "0"}))

@app.route('/email_res_id', methods = ['POST'])
def email_res_id():
    res_id, mail_addr = request.json["reservation_id"], request.json["email_id"]
    res_id_mail(mail_addr, res_id)
    return jsonify({"returnCode" : "0"})

@app.route('/sms_res_id', methods = ['POST'])
def sms_res_id():
    res_id, phoneno = request.json["reservation_id"], request.json["phone_no"]
    res_id_sms(phoneno, res_id)
    return jsonify({"returnCode" : "0"})

@app.route('/dlg_logging', methods = ['POST'])
def dlg_logging():
    global res
    # Trusted Connection to Named Instance
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:chatbot-accelerator.database.windows.net,1433;Database=chatbot_db;Uid=serverAdmin;Pwd=ai2ai2ai@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    usr_prompt = request.json["user_input_var"]
    bot_response = request.json["bot_input_var"]
    session_id = request.json["session_id"]
    untrained_questions = request.json["custom_questions"]
    now = datetime.datetime.now()
    time_stamp = now.strftime('%Y-%m-%d %H:%M:%S')
    bot = bot_response.strip("####").split("####")[:-1]
    user = usr_prompt.strip("####").split("####")[:-1]
    conversation = []
    intents = []
    for i in range(max(len(bot), len(user))):
        if i<len(bot):
            conversation.extend(["Bot: ", bot[i], "\n"])
            if "welcome" in bot[i].lower():
                intent = bot[i].lower().replace('welcome to', '').replace('welcome back to', '').replace('!', '').strip()
                intents.extend([intent])
        if i<len(user):
            if user[i]!="_":
                conversation.extend(["User: ", user[i], "\n"])
                
    intents = ", ".join(list(set(intents)))
    conversation = "".join(conversation).strip()
    cursor=connection.cursor()
    # insert_query = f"insert into [dbo].[nuance_conversation_log](usr_prompt, bot_response, session_id, time_stamp) values ('{str(usr_prompt)}','{str(bot_response)}','{session_id}','{time_stamp}')"
    insert_query = f"insert into [dbo].[nuance_conversation_log](usr_prompt, bot_response, session_id, time_stamp, conversation, intents, untrained_questions) values (?, ?, ?, ?, ?, ?, ?)"
    
    print("insert_query======================\n")
    print(insert_query)
    cursor.execute(insert_query, str(usr_prompt),str(bot_response),session_id,time_stamp, str(conversation), str(intents), str(untrained_questions))
    cursor.commit()
    connection.close()
    return (jsonify({"status":"complaint has been stored successfully", "returnCode" : "0"}))

# driver function
if __name__ == '__main__':
#   gunicorn --bind=0.0.0.0 --timeout 600 app:app --worker-class=gevent
    app.run(host= '0.0.0.0',debug=True, port=8080)
