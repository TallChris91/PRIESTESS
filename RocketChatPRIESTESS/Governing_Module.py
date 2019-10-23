from Lookup_Module import ConvertWorkbook
from Template_Filler_Module import TemplateReplacement
import Answer_Understanding_Module
import time
import os
import random
from spellchecker import SpellChecker
from spacy.lang.nl import Dutch
import regex as re
import Chat_Interaction_Module
import Ruleset_Module
from rocketchat_API.rocketchat import RocketChat
import pickle
import sys
import Save_Chat_Module
import Participant_Number_Module
import json

def IdleWait(rocket, username, legend, templates, chatid):
    # First, quietly wait for a reply that turns the chatbot on
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 5, 43200, chatid)
    if response == 'chat=start':
        Chat_Interaction_Module.SendMessage(rocket, 'Chatbot opgestart. Berichten worden verwijderd en het gesprek begint over 10 seconden.', chatid)
        time.sleep(10)
        Ruleset_Module.deletechatmodule(rocket, chatid)
        # Find the templates
        idx = legend.index('Introduction (question)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
    else:
        Chat_Interaction_Module.SendMessage(rocket, 'Onbekend startcommando. Bericht wordt verwijderd over 5 seconden.', chatid)
        time.sleep(5)
        Ruleset_Module.deletechatmodule(rocket, chatid)
        IdleWait(rocket, username, legend, templates, chatid)

#Not a great function name, but eh...
def IntroductionAnswerandResponse(rocket, legend, templates, spellname, nlnlp, chatid, clarificationasked='n'):
    # First, we'll wait for max. 3 minutes for a response
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 180, chatid)
    #Then use the FindName module to find the name in the response
    name = Answer_Understanding_Module.FindName(response, spellname, nlnlp)

    # If no name could be found
    if (name == None) and (clarificationasked == 'n'):
        # Get the template for repeat question, and ask that
        idx = legend.index('Introduction (repeat question)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        # And wait for a response to the name-question again, while making sure that we won't ask for clarification again
        IntroductionAnswerandResponse(rocket, legend, templates, spellname, nlnlp, chatid, 'y')
    # If the participant still could not give a name after the repetition, assume that they're refusing to answer
    else:
        if ((name == None) and (clarificationasked == 'y')) or (name == 'refuseName'):
            # Find the templates
            idx = legend.index('Introduction (response; no name given)')
            # Select a random template from the list
            selectedtemplate = random.choice(templates[idx])
            # Now let's fill the template up
            filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
        else:
            # Find the templates
            idx = legend.index('Introduction (response; name given)')
            # Select a random template from the list
            selectedtemplate = random.choice(templates[idx])
            # Now let's fill the template up
            filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, name=name)

        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        # Now move onto the next question
        time.sleep(2)
        # For place of residence we just have one question and category: Place of Residence (question). Get the index where the templates are
        #idx = legend.index('Place of Residence (question)') #Omitted for final version
        idx = legend.index('Previous Lowlands (question)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, name=name)
        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        # Return the name for future questions
        return name

def PreviousLLandResponse(rocket, legend, templates, spellnl, nlnlp, chatid, clarificationasked='n'):
    # First, we'll wait for max. 2 minutes for a response
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 120, chatid)
    # Extract the name out of the message
    firsttime = Answer_Understanding_Module.FindPrevious(response, spellnl, nlnlp)
    # If no answer to the previous Lowlands could be found
    if (firsttime == None) and (clarificationasked == 'n'):
        # Get the template for repeat question, and ask that
        idx = legend.index('Previous Lowlands (repeat question)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        # And await the new answer, while ensuring that the repeat question is not asked again
        PreviousLLandResponse(rocket, legend, templates, spellnl, nlnlp, chatid, 'y')
    # If the participant still could not give a name after the repetition, assume that they're refusing to answer
    else:
        if ((firsttime == None) and (clarificationasked == 'y')) or (firsttime == 'RefuseTime'):
            # Find the templates
            idx = legend.index('Previous Lowlands (response; no information given)')
        elif firsttime == 'BeenBefore':
            # Find the templates
            idx = legend.index('Previous Lowlands (response; not the first time)')
        else:
            # Find the templates
            idx = legend.index('Previous Lowlands (response; first time)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        return firsttime

def LLOpinionandResponse(rocket, legend, templates, spellnl, nlnlp, chatid):
    # First, we'll wait for max. 2 minutes for a response
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 120, chatid)
    # Extract the sentiment out of the message
    opinion = Answer_Understanding_Module.FindOpinion(response, spellnl, nlnlp)
    # If the sentiment analysis says the response is positive
    if opinion == 'Positive':
        # Get the template for positive response, and use that
        idx = legend.index('Previous Lowlands (response; positive sentiment)')
    # If the sentiment analysis says the response is negative
    elif opinion == 'Negative':
        # Find the templates
        idx = legend.index('Previous Lowlands (response; negative sentiment)')
    else:
        # Find the templates
        idx = legend.index('Previous Lowlands (response; no clear sentiment)')
    # Select a random template from the list
    selectedtemplate = random.choice(templates[idx])
    # Now let's fill the template up
    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
    # And send the message
    Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
    # Now move onto the next question
    time.sleep(2)
    # Now ask the next question about the artists on the festival
    idx = legend.index('Artist Talk (question)')
    # Select a random template from the list
    selectedtemplate = random.choice(templates[idx])
    # Now let's fill the template up
    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
    # And send the message
    Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
    return opinion

def ArtistandResponse(rocket, legend, templates, spellartist, nlnlp, artistlist, writerlist, movielist, otherlist, artistdict, writerdict, moviedict, otherdict, chatid, clarificationasked='n'):
    # First, we'll wait for max. 2 minutes for a response
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 120, chatid)
    # Extract the artist out of the message and the domain of the artist
    artist, domain = Answer_Understanding_Module.FindArtist(response, spellartist, nlnlp, artistlist, writerlist, movielist, otherlist, artistdict, writerdict, moviedict, otherdict)
    # If no artist could be found
    if (artist == None) and (clarificationasked == 'n'):
        # Get the template for repeat question, and ask that
        idx = legend.index('Artist Talk (repeat question)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        # And await the new answer, while ensuring that the repeat question is not asked again
        ArtistandResponse(rocket, legend, templates, spellartist, nlnlp, artistlist, writerlist, movielist, otherlist, artistdict, writerdict, moviedict, otherdict, chatid, 'y')
    # If the participant still could not give an artist from the line up after the repetition, assume that they're refusing to answer
    else:
        if ((artist == None) and (clarificationasked == 'y')) or (artist == 'refuseArtist'):
            # Find the templates
            idx = legend.index('Artist Talk (not found)')
            # Select a random template from the list
            selectedtemplate = random.choice(templates[idx])
            # Now let's fill the template up
            filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
            #Make the artist a None type (for the next question, so that it only asks an opinion if a viable artist was given here)
            artist = None
            # And send the message
            Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
            #And take a break because we skip the opinion question
            time.sleep(2)
        # If the participant gave a viable artist
        else:
            if domain == 'music':
                # Get info about the artist
                album, track, genre = Answer_Understanding_Module.artist_search(os.getcwd() + '/Databases/ArtistsDB.db', artist)
                # Find the templates
                idx = legend.index('Artist Talk (musician response)')
                # Select a random template from the list
                selectedtemplate = random.choice(templates[idx])
                # Now let's fill the template up
                filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, artist=artist, album=album, song=track, genre=genre)
            elif domain == 'movies':
                actor, genre, director = Answer_Understanding_Module.movie_search(os.getcwd() + '/Databases//ArtistsDB.db', artist)
                # Find the templates
                idx = legend.index('Artist Talk (movie response)')
                # Select a random template from the list
                selectedtemplate = random.choice(templates[idx])
                # Now let's fill the template up
                filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, artist=artist, actor=actor, director=director, genre=genre)
            elif domain == 'books':
                book = Answer_Understanding_Module.writer_search(os.getcwd() + '/Databases//ArtistsDB.db', artist)
                # Find the templates
                idx = legend.index('Artist Talk (writer response)')
                # Select a random template from the list
                selectedtemplate = random.choice(templates[idx])
                # Now let's fill the template up
                filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, artist=artist, book=book)
            else:
                genre, show = Answer_Understanding_Module.other_search(os.getcwd() + '/Databases//ArtistsDB.db', artist)
                # Find the templates
                idx = legend.index('Artist Talk (other response; no info)')
                # Select a random template from the list
                selectedtemplate = random.choice(templates[idx])
                #If there are shows associated with the act, make it possible to also choose the category that talks about shows
                if show != None:
                    # Find the templates
                    idx = legend.index('Artist Talk (other response; with info)')
                    # Select a random template from the list
                    selectedtemplateshow = random.choice(templates[idx])
                    #Add the selected template to the selected no info template
                    alltemplates = [selectedtemplate] + [selectedtemplateshow]
                    #Select one of these two randomly
                    newselectedtemplate = random.choice(alltemplates)
                    #And fill 'er up
                    filledtemplate, gapfiller = TemplateReplacement(newselectedtemplate, artist=artist, genre=genre, show=show)
                else:
                    #If there was no show associated with the act, just use the show and domain as info for the template
                    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, artist=artist, genre=genre)
            # And send the message
            Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        return artist

def ArtistOpinionandResponse(rocket, legend, templates, spellnl, nlnlp, name, artist, chatid):
    if (artist != None) and (artist != 'refuseArtist'):
        # First, we'll wait for max. 2 minutes for a response
        response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 120, chatid)
        # Extract the sentiment out of the message
        opinion = Answer_Understanding_Module.FindOpinion(response, spellnl, nlnlp)
        # If the sentiment analysis says the response is positive
        if opinion == 'Positive':
            # Get the template for positive response, and use that
            idx = legend.index('Artist Talk (positive answer)')
        # If the sentiment analysis says the response is negative
        elif opinion == 'Negative':
            # Find the templates
            idx = legend.index('Artist Talk (negative answer)')
        # If the sentiment analysis says the response is neutral
        else:
            # Find the templates
            idx = legend.index('Artist Talk (no clear sentiment)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
        # And send the message
        Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
        # Now move onto the next question
        time.sleep(2)
    # Now ask the next question about the artists on the festival
    idx = legend.index('Secret (question)')
    # Select a random template from the list
    selectedtemplate = random.choice(templates[idx])
    # Now let's fill the template up
    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, name=name)
    # And send the message
    Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)

def SecretandResponse(rocket, legend, templates, spellnl, nlnlp, liwcdict, liwcdictnodiacritics, chatid):
    # First, we'll wait for max. 2 minutes for a response
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 120, chatid)
    # Extract the LIWC category out of the message
    category = Answer_Understanding_Module.LIWCFeatures(response, liwcdict, liwcdictnodiacritics, spellnl, nlnlp)
    # Find the templates
    if (category == 'liwc30') or (category == 'liwc31') or (category == 'liwc32') or (category == 'liwc33') or (category == 'liwc34') \
            or (category == 'liwc35'):
        idx = legend.index('LIWC (response; affective processes)')
    elif (category == 'liwc40') or (category == 'liwc41') or (category == 'liwc42'):
        idx = legend.index('LIWC (response; social processes)')
    elif (category == 'liwc43') or (category == 'liwc44') or (category == 'liwc71') or (category == 'liwc72') \
            or (category == 'liwc73'):
        idx = legend.index('LIWC (response; gender and body references)')
    elif (category == 'liwc74'):
        idx = legend.index('LIWC (response; ingestion)')
    elif (category == 'liwc81') or (category == 'liwc82') or (category == 'liwc83') or (category == 'liwc84'):
        idx = legend.index('LIWC (response; drives)')
    elif (category == 'liwc85'):
        idx = legend.index('LIWC (response; risk)')
    elif (category == 'liwc110') or (category == 'liwc111') or (category == 'liwc112') or (category == 'liwc113') \
            or (category == 'liwc114') or (category == 'liwc115'):
        idx = legend.index('LIWC (response; personal concerns)')
    elif (category == 'liwc121'):
        idx = legend.index('LIWC (response; swear)')
    else:
        idx = legend.index('LIWC (response; no topic)')
    # Select a random template from the list
    selectedtemplate = random.choice(templates[idx])
    # Now let's fill the template up
    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, liwccat=category)
    # And send the message
    Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)

def SecretOpinionandResponse(rocket, legend, templates, spellnl, nlnlp, liwcdict, liwcdictnodiacritics, chatid, condition):
    # First, we'll wait for max. 2 minutes for a response
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 120, chatid)
    if condition == '1':
        emotioncategory = Answer_Understanding_Module.LIWCFeatures(response, liwcdict, liwcdictnodiacritics, spellnl, nlnlp, 'y')
        if (emotioncategory == 'liwc32') or (emotioncategory == 'liwc33') or (emotioncategory == 'liwc34') or (emotioncategory == 'liwc35'):
            idx = legend.index('LIWC (emotion response; negative emotion)')
        elif emotioncategory == 'liwc31':
            idx = legend.index('LIWC (emotion response; positive emotion)')
        else:
            idx = legend.index('LIWC (emotion response; no clear emotion)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, liwccat=emotioncategory)
    else:
        idx = legend.index('LIWC (emotion response; low condition)')
        # Select a random template from the list
        selectedtemplate = random.choice(templates[idx])
        # Now let's fill the template up
        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
    # And send the message
    Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)

def Goodbye(rocket, legend, templates, participantnumber, chatid, condition):
    # First, we'll wait for max. 2 minutes for a response
    response = Chat_Interaction_Module.WaitForReply_par(rocket, 1, 120, chatid)
    # End the conversation
    idx = legend.index('Goodbye')
    # Select a random template from the list
    selectedtemplate = random.choice(templates[idx])
    # Now let's fill the template up
    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
    # And send the message
    Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)
    # Wait for a bit
    time.sleep(2)
    # And use the participant number to generate the final message
    surveylink = '<qualtrics_link>'
    newlink = surveylink + '?id=' + str(participantnumber) + '&condition=' + condition
    # End the conversation
    idx = legend.index('Survey link')
    # Select a random template from the list
    selectedtemplate = random.choice(templates[idx])
    # Now let's fill the template up
    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, link=newlink)
    # And send the message
    Chat_Interaction_Module.SendMessage(rocket, filledtemplate, chatid)

def Chatbot_Govern():
    currentpath = os.getcwd()
    nlnlp = Dutch()
    nlnlp.add_pipe(nlnlp.create_pipe('sentencizer'))
    legend, templates = ConvertWorkbook(currentpath + '/Templates/All_Templates.xlsx')
    spellnl = SpellChecker(language=None)
    spellnl.word_frequency.load_dictionary(currentpath + '/Databases/nlsubtiel2.json')
    spellname = SpellChecker(language=None)
    with open(currentpath + '/Databases/voornamen.ner', 'r', encoding='utf-8') as f:
        firstnames = f.readlines()
    firstnames = [re.sub(r'\n', '', x) for x in firstnames]
    spellname.word_frequency.load_words(['ik', 'ben', 'naam', 'is', 'heet', 'noemen', 'mij', 'de', 'naam', 'ze', 'word', 'genoemd', 'vertellen',
                                       'zeggen', 'voorstellen', 'geven', 'vertel', 'zeg', 'stel', 'geef', 'beantwoorden', 'beantwoord', 'antwoorden',
                                         'antwoord', 'niet', 'niets', 'niks', 'aan', 'geheim', 'weiger'] + firstnames)

    with open(currentpath + '/Databases/artistlist.pkl', 'rb') as f:
        artistlist = pickle.load(f)

    with open(currentpath + '/Databases/writerlist.pkl', 'rb') as f:
        writerlist = pickle.load(f)

    with open(currentpath + '/Databases/movielist.pkl', 'rb') as f:
        movielist = pickle.load(f)

    with open(currentpath + '/Databases/otherlist.pkl', 'rb') as f:
        otherlist = pickle.load(f)

    with open(currentpath + '/Databases/artistdict.pkl', 'rb') as f:
        artistdict = pickle.load(f)

    with open(currentpath + '/Databases/writerdict.pkl', 'rb') as f:
        writerdict = pickle.load(f)

    with open(currentpath + '/Databases/moviedict.pkl', 'rb') as f:
        moviedict = pickle.load(f)

    with open(currentpath + '/Databases/otherdict.pkl', 'rb') as f:
        otherdict = pickle.load(f)

    with open(currentpath + '/Databases/alllist.pkl', 'rb') as f:
        alllist = pickle.load(f)

    artistlist2 = [x.lower() for x in artistlist]
    writerlist2 = [x.lower() for x in writerlist]
    movielist2 = [x.lower() for x in movielist]
    otherlist2 = [x.lower() for x in otherlist]
    spellartist = SpellChecker(language=None)
    spellartist.word_frequency.load_words(artistlist2 + writerlist2 + movielist2 + otherlist2 + alllist + ['vertellen', 'zeggen', 'geven', 'vertel', 'zeg', 'geef', 'beantwoord', 'beantwoorden', 'antwoord', 'antwoorden', 'niets', 'niks', 'niet', 'geheim', 'weiger', 'aan'])
    liwcdict, liwcdictnodiacritics = Answer_Understanding_Module.LIWCdict(currentpath)

    with open(os.getcwd() + '/Datadict.json') as data_file:
        datadict = json.load(data_file)

    chatid = datadict['chatid']
    condition = datadict['condition']
    lowerbound = datadict['lowerbound']
    password = datadict['password']
    upperbound = datadict['upperbound']
    username = datadict['username']

    rocket = RocketChat(username, password, server_url='<server_url>')

    print('All preperation is done!')

    def Conversation_Module():
        #Wait for the module to be activated and after activation ask the first question about name
        IdleWait(rocket, username, legend, templates, chatid)
        #Retrieve the name and ask about place of living
        name = IntroductionAnswerandResponse(rocket, legend, templates, spellname, nlnlp, chatid)
        #Retrieve information about the previous Lowlands experience and ask about their opinion about last time/this time
        PreviousLLandResponse(rocket, legend, templates, spellnl, nlnlp, chatid)
        #Retrieve information about the opinion on Lowlands and ask about favorite artist performance on Lowlands
        LLOpinionandResponse(rocket, legend, templates, spellnl, nlnlp, chatid)
        # Retrieve information about the opinion on Lowlands and ask about favorite artist performance on Lowlands
        artist = ArtistandResponse(rocket, legend, templates, spellartist, nlnlp, artistlist, writerlist, movielist, otherlist, artistdict, writerdict, moviedict, otherdict, chatid)
        # Retrieve information about the opinion on the artist and ask about the secret
        ArtistOpinionandResponse(rocket, legend, templates, spellnl, nlnlp, name, artist, chatid)
        if condition == '1':
            #Retrieve information about the secret and ask about their feelings regarding the secret
            SecretandResponse(rocket, legend, templates, spellnl, nlnlp, liwcdict, liwcdictnodiacritics, chatid)
        #Retrieve information about their feelings on the secret and ask if they want to share anything more about it
        SecretOpinionandResponse(rocket, legend, templates, spellnl, nlnlp, liwcdict, liwcdictnodiacritics, chatid, condition)
        #Retrieve a new (unused) participantnumber
        participantnumber = Answer_Understanding_Module.GetParticipantNumber(lowerbound, upperbound)
        #End the conversation
        Goodbye(rocket, legend, templates, participantnumber, chatid, condition)

        #Now that we've had it all, it's time to turn off the chatbot
        def Idle_End():
            # Wait for a command that tells us what to do here
            response = Chat_Interaction_Module.WaitForReply_par(rocket, 5, 43200, chatid)
            if response == 'chat=end':
                Chat_Interaction_Module.SendMessage(rocket, 'Het gesprek wordt opgeslagen. Berichten worden verwijderd over 5 seconden.', chatid)
                time.sleep(5)
                history = rocket.groups_history(chatid, count=100).json()
                messages = history['messages']
                Save_Chat_Module.convertformat(messages, rocket, chatid, participantnumber, condition)
                Ruleset_Module.deletechatmodule(rocket, chatid)
                Conversation_Module()
            elif response == 'chat=kill':
                Chat_Interaction_Module.SendMessage(rocket, 'De chatbot wordt afgesloten en het gesprek wordt opgeslagen. Berichten worden verwijderd over 5 seconden.', chatid)
                time.sleep(5)
                history = rocket.groups_history(chatid, count=100).json()
                messages = history['messages']
                Save_Chat_Module.convertformat(messages, rocket, chatid, participantnumber, condition)
                Ruleset_Module.deletechatmodule(rocket, chatid)
                sys.exit()
            else:
                Chat_Interaction_Module.SendMessage(rocket, 'Ongeldig eindcommando.', chatid)
                Idle_End()

        Idle_End()


    Conversation_Module()

Chatbot_Govern()