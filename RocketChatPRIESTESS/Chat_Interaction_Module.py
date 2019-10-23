import Ruleset_Module
import time
from multiprocessing.pool import ThreadPool

def WaitForReply(rocket, waittime, totaltime, chatid):
    # Let's wait for a reply
    # The while loop runs for the amount of seconds indicated by totaltime if nothing happens
    # Check every three seconds if a reply was made
    mustend = time.time() + totaltime
    recent_message = ''
    while time.time() < mustend:
        #Try to obtain the chat history from the api, but sometimes it doesn't respond. Then we'll just wait 3 seconds and try again.
        try:
            history = rocket.groups_history(chatid, count=100).json()
            messages = history['messages']
            # If no recent post was made, take a nap
            if Ruleset_Module.checklastmessage(messages, waittime) == False:
                time.sleep(waittime)
            else:
                # As a heuristic, we're going to look at the first message that was posted after the chatbot's most recent post
                recent_message = Ruleset_Module.firstresponse(messages)
                break
        except KeyError:
            time.sleep(waittime)

    return recent_message

def WaitForReply_par(rocket, waittime, totaltime, chatid):
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(WaitForReply, (rocket, waittime, totaltime, chatid))
    return_val = async_result.get()
    return return_val

def SendMessage(rocket, message, chatid):
    # Post a message, format: MessageContent, roomId, alias
    rocket.chat_post_message(message, chatid)