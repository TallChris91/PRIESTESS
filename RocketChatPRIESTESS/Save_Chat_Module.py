from datetime import datetime
from pytz import timezone
import regex as re
import os
import pickle

def getdatetime(datestring):
    #Get the date as e.g. 22-04-2019
    daytemplate = '%d-%m-%Y'
    #Get the time as 14:39:11
    timetemplate = '%H:%M:%S'
    #Original timestring is like 2019-04-07T12:39:11.422Z, so let's remove the milliseconds first (the stuff after the period)
    datestring = re.search(r'^(.*?)\.', datestring).group(1)
    #Convert the string to a datetime object
    datetime_obj = datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S")
    #Rocket chat saves the time as UTC time, so add that information to the datetime object
    datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))
    #Convert the UTC time to the Dutch timezone
    datetime_here = datetime_obj_utc.astimezone(timezone('Europe/Berlin'))
    #Return a tuple with a datestring and a timestring
    return datetime_here.strftime(daytemplate), datetime_here.strftime(timetemplate)

def convertcite(message):
    citetext = message['attachments'][0]['text']
    author = message['attachments'][0]['author_name']
    senddate, sendtime = getdatetime(message['attachments'][0]['ts'])
    return 'cite([' + author + ' (' + sendtime + '): ' + citetext + '])'

def getchatname(rocket, roomid):
    chatinfo = rocket.groups_info(roomid).json()
    chatinfo = chatinfo['group']['name']
    return chatinfo


def convertformat(messages, rocket, roomid, participantnumber, condition):
    #Sort messages by the time they were posted
    data_sorted = sorted(messages, key=lambda k: k['ts'])
    chatstring = ''
    for message in data_sorted:
        un = message['u']['username']
        msg = message['msg']
        if ('attachments' in message) and (len(message['attachments']) > 0) and ('text' in message['attachments'][0]):
            newcite = convertcite(message)
            msg = re.sub(r'\[(.*?)\)', newcite, msg)
        senddate, sendtime = getdatetime(message['ts'])
        if chatstring == '':
            chatstring += 'Date: ' + senddate + '\n'
            chatstring += 'Chat: ' + getchatname(rocket, roomid) + '\n'
            chatstring += 'Participant number: ' + str(participantnumber) + '\n'
            chatstring += 'Condition: ' + str(condition) + '\n'
            chatstring += '\n'
        chatstring += un + ' (' + sendtime + '): ' + msg + '\n'

    currentpath = os.getcwd()
    with open(currentpath + '/Conversations/Pnumber_' + str(participantnumber) + '_condition_' + str(condition) + '.txt', 'wb') as f:
        f.write(bytes(chatstring, 'UTF-8'))

    with open(currentpath + '/Conversations/Pnumber_' + str(participantnumber) + '_condition_' + str(condition) + '.pkl', 'wb') as f:
        pickle.dump(data_sorted, f)

    return chatstring, data_sorted