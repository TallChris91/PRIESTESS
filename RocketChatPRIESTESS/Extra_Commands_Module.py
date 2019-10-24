from datetime import datetime
from pytz import timezone
import regex as re
import time

def getdatetime(datestring):
    #Original timestring is like 2019-04-07T12:39:11.422Z, so let's remove the milliseconds first (the stuff after the period)
    #Convert the string to a datetime object
    datetime_obj = datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S.%fZ")
    #Rocket chat saves the time as UTC time, so add that information to the datetime object
    datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))
    #Convert the UTC time to the Dutch timezone
    datetime_here = datetime_obj_utc.astimezone(timezone('Europe/Berlin'))
    #And remove the timezone info from the datetime object
    datetime_here = datetime_here.replace(tzinfo=None)
    #Return the datetime object
    return datetime_here

def checklastmessage(messages, differenceminimum):
    # Sort messages by the time they were posted
    data_sorted = sorted(messages, key=lambda k: k['ts'])
    if data_sorted == []:
        return False
    #The last message in the list is the most recent
    recent_message = data_sorted[-1]
    #Check if the last message was sent by the participant
    if not 'alias' in recent_message: #VERANDER DIT STRAKS NAAR if recent_message['u']['username'] != PRIEST:
        #Get a datetime object with the time the last message was posted
        sendtime = getdatetime(recent_message['ts'])
        #Get the current time
        present = datetime.now()
        #Calculate the number of seconds that has past the last message
        difference = (present - sendtime).total_seconds()
        #If more than the pre-selected minimum seconds have past, return True
        if difference > differenceminimum:
            return True
        else:
            return False
    else:
        return False

def firstresponse(messages):
    # Sort messages by the time they were posted
    data_sorted = sorted(messages, key=lambda k: k['ts'], reverse=True)
    #Go over the messages, most recent one first
    for idx, message in enumerate(data_sorted):
        #When you find the most recent message that is by PRIEST
        if ('alias' in message) and (len(data_sorted) > 1):
            #Return the message that was posted directly after the most recent PRIEST post
            return data_sorted[idx-1]['msg']
        elif (len(data_sorted) == 1): #Or if there is only one message, return it
            return data_sorted[idx]['msg']


def deletechatmodule(rocket, chatid):
    #Obtain the chat history
    while True:
        try:
            history = rocket.groups_history(chatid, count=100).json()
            break
        except KeyError:
            time.sleep(3)
    #And the messages
    messages = history['messages']
    #And the ids of these messages
    idlist = [x['_id'] for x in messages]
    for id in idlist:
        # Delete messages, format: roomId, messageId
        rocket.chat_delete(chatid, id)