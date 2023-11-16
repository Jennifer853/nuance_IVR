# Using flask to make an api
# import necessary libraries and functions
import json
from flask import Flask, jsonify, request
import os
import pyodbc
from azure.communication.sms import SmsClient
from azure.communication.email import EmailClient


# creating a Flask app
app = Flask(__name__)

# headers = {
#   'Ocp-Apim-Subscription-Key': 'a804d41345194b1ea518cc6424324d9e',
#   'Content-Type': 'application/json'
# }

# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET'])
def home():
    return jsonify({'sentiment': "API for sentiment"})

def res_id_sms(message, phoneno, from_number):
    if from_number == '+18552368457':
        sms_client = SmsClient.from_connection_string("endpoint=https://chatbotcommunications.communication.azure.com/;accesskey=H+GEiikyhWWcGMXUkxxMGX7/DOnNyQXV4wlqzlVUtVzyGWNu4wdaJn36yMtLc+JPqORrS2iAE9uija3wwr66Eg==")
    else:
        sms_client = SmsClient.from_connection_string("endpoint=https://dcs-nuance-2way-communication.unitedstates.communication.azure.com/;accesskey=q7lBgD6uijtCB7J7EtqZjY+QvxlGV2umei0UOGJzMNaTo2fdSiLHVNC94H/5mBentA+lVnpmOkjgHQGRYFJyIw==")

    try:
        sms_responses = sms_client.send(
            from_=from_number,#"",
            to="+1"+phoneno.replace('-',''),
            message=message,
            enable_delivery_report=True, # optional property
            tag="custom-tag") # optional property
        for sms_response in sms_responses:
            if (sms_response.successful):
                print("Message with message id {} was successful sent to {}"
                      .format(sms_response.message_id, sms_response.to))
            else:
                print("Message failed to send to {} with the status code {} and error: {}"
                      .format(sms_response.to, sms_response.http_status_code, sms_response.error_message))
    except Exception as ex:
        print('Exception:')
        print(ex)
  
@app.route('/sms_res_id', methods = ['POST'])
def sms_res_id():
    phoneno = request.json["phone_no"]
    message = request.json["message"]
    from_number = request.json["from_number"]
    res_id_sms(message, phoneno, from_number)

    return jsonify({"returnCode" : "0"})

@app.route('/email', methods = ['POST'])
def res_id_mail():
    subject_email = request.json["subject_email"]
    body_email = request.json["body_email"]
    to_email_id = request.json["to_email_id"]

    try:
        connection_string = "endpoint=https://chatbotcommunications.communication.azure.com/;accesskey=H+GEiikyhWWcGMXUkxxMGX7/DOnNyQXV4wlqzlVUtVzyGWNu4wdaJn36yMtLc+JPqORrS2iAE9uija3wwr66Eg=="
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": "DoNotReply@9d61eb9d-901e-4349-95b7-bdab02bc9bef.azurecomm.net",
            "recipients":  {
                "to": [{"address": to_email_id }],
            },
            "content": {
                "subject": subject_email,
                # "plainText": "Hello world via email.",
                "html": body_email,
            }
        }

        client.begin_send(message)
        email_status = 'sent'
        # result = poller.result()

    except Exception as ex:
        print(ex)
        email_status = 'exception'
    
    return jsonify({"returnCode" : "0", "email_status" : email_status})


# driver function
if __name__ == '__main__':
#   gunicorn --bind=0.0.0.0 --timeout 600 app:app --worker-class=gevent
    app.run(host= '0.0.0.0',debug=True, port=8080)
