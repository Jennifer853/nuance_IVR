import os
from azure.communication.email import EmailClient
import pyodbc
from azure.communication.sms import SmsClient

def res_id_sms(phoneno, res_id):
    checkin, checkout, room_txt, res_id, ext_txt = select_info_with_res_id(res_id)
    message = f"""[Paradise Resort] We are pleased to confirm your hotel reservation for {checkin} to {checkout} for {room_txt}. Your reservation ID is {res_id}. {ext_txt} Thank you for choosing us. We look forward to welcoming you!"""
    print(message)
    sms_client = SmsClient.from_connection_string("endpoint=https://chatbotcommunications.communication.azure.com/;accesskey=H+GEiikyhWWcGMXUkxxMGX7/DOnNyQXV4wlqzlVUtVzyGWNu4wdaJn36yMtLc+JPqORrS2iAE9uija3wwr66Eg==")
    sms_responses = sms_client.send(
    from_= "",
    to="+1"+phoneno.replace('-',''),
    message=message,
    enable_delivery_report=True, # optional property
    tag="custom-tag") # optional property

def select_info_with_res_id(res_id):
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:chatbot-accelerator.database.windows.net,1433;Database=chatbot_db;Uid=serverAdmin;Pwd=ai2ai2ai@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor=connection.cursor()
    query = f"select * from [dbo].[nuance_reservation] where res_id={res_id}"
    cursor=connection.cursor()
    cursor.execute(query)
    row = cursor.fetchall()[0]
    n_rooms = row[2]
    checkin,checkout  = row[3].strftime('%Y-%m-%d'), row[4].strftime('%Y-%m-%d')
    extra = list(set([i.strip() for i in row[5].split(',')]))
    room_type = f' {row[6]} '.strip().lower()
    extra.remove("room")
    if room_type!='none':
        room_txt, ext_txt = f"1 {room_type} room", ""
        if n_rooms >1:
            room_txt = f"{n_rooms} {room_type} rooms"
    else:
        room_txt, ext_txt = "1 room", ""
        if n_rooms >1:
            room_txt = f"{n_rooms} rooms"
    if len(extra)==1:
        ext_txt =  extra[0]
    elif len(extra)>1:
        ext_txt = ', '.join(extra[:-1])+" and " + extra[-1]
    if extra:
        ext_txt = f"During your trip, you also booked our {ext_txt}, hope you enjoy our services!"
    return checkin, checkout, room_txt, res_id, ext_txt

def res_id_mail(mail_addr, res_id):
    checkin, checkout, room_txt, res_id, ext_txt = select_info_with_res_id(res_id)
    connection_string = "endpoint=https://chatbotcommunications.communication.azure.com/;accesskey=H+GEiikyhWWcGMXUkxxMGX7/DOnNyQXV4wlqzlVUtVzyGWNu4wdaJn36yMtLc+JPqORrS2iAE9uija3wwr66Eg=="
    email_client = EmailClient.from_connection_string(connection_string)

    message = {
        "content": {
            "subject": "Confirm Your Reservation for Paradise Resort",
            "plainText": "This is the body",
            "html": f"""
    <html>  
    <head>  
        <meta charset="UTF-8">  
        <title>Your Reservation Code for Paradise Resort</title>  
    </head>  
    <body>  
        <p>Dear Customer,</p>  
        <p>Thank you for choosing Paradise Resort for your upcoming stay. We are thrilled to have you as our guest and can't wait to provide you with a memorable experience.</p>  
        <p>We have confirmed your reservation for <strong>{checkin}</strong> to <strong>{checkout}</strong> for <strong>{room_txt}</strong>. Your reservation code is <strong>{res_id}</strong>. Please keep this code safe, as it will be required during check-in.</p>  
        <p>{ext_txt}<p>
        <p>Should you have any questions or concerns regarding your reservation, please don't hesitate to contact us. We are always here to help and ensure your stay is comfortable and enjoyable.</p>  
        <p>We look forward to welcoming you soon.</p>  
        <p>Best regards,</p>  
        <p>Paradise Resort Team</p>  
    </body>  
    </html> 
    """
        },
        "recipients": {
            "to": [
                {
                    "address": f"<{mail_addr}>",
                    "displayName": "Customer Name"
                }
            ]
        },
        "senderAddress": "DoNotReply@9d61eb9d-901e-4349-95b7-bdab02bc9bef.azurecomm.net"
    }
    poller = email_client.begin_send(message)

