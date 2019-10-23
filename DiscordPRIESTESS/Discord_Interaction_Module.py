from Lookup_Module import ConvertWorkbook
from Template_Filler_Module import TemplateReplacement
import Answer_Understanding_Module
import discord
import time
import os
import random
from spellchecker import SpellChecker
from spacy.lang.nl import Dutch
import csv
from unidecode import unidecode
import regex as re
import pickle
import json
from datetime import date
import sys

def replymessage():
    currentpath = os.getcwd()

    with open(os.getcwd() + '/Datadict.json') as data_file:
        datadict = json.load(data_file)

    chatid = datadict['chatid']
    condition = datadict['condition']
    lowerbound = datadict['lowerbound']
    upperbound = datadict['upperbound']
    token = datadict['token']

    chatbot = 'n'
    if condition == '1':
        topics = ['IntroductionResponse', 'PreviousLowlandsResponse', 'LowlandsOpinionResponse', 'ArtistTalkResponse',
                  'ArtistTalkOpinionResponse', 'SecretTopicResponse', 'SecretTopicEmotionResponse', 'EndofConversation', 'IdleChat']
    else:
        topics = ['IntroductionResponse', 'PreviousLowlandsResponse', 'LowlandsOpinionResponse', 'ArtistTalkResponse',
                  'ArtistTalkOpinionResponse', 'SecretTopicEmotionResponse', 'EndofConversation', 'IdleChat']
    currenttopic = 0
    name = ''
    firsttime = ''
    clarificationasked = 'n'
    artistmentioned = 'n'
    participantnumber = ''
    nlnlp = Dutch()
    nlnlp.add_pipe(nlnlp.create_pipe('sentencizer'))
    legend, templates = ConvertWorkbook(currentpath + '/Templates/All_Templates.xlsx')
    spellnl = SpellChecker(language=None)
    spellnl.word_frequency.load_dictionary(currentpath + '/Databases/nlsubtiel2.json')
    spellname = SpellChecker(language=None)
    with open(os.getcwd() + '/Databases/voornamen.ner', 'r', encoding='utf-8') as f:
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
    spellartist.word_frequency.load_words(artistlist2 + writerlist2 + movielist2 + otherlist2 + alllist + ['vertellen', 'zeggen', 'geven', 'vertel', 'zeg', 'geef', 'beantwoord', 'beantwoorden', 'antwoord', 'antwoorden', 'niets', 'niks', 'niet', 'geheim', 'weiger', 'aan', 'geen'])
    liwcdict, liwcdictnodiacritics = Answer_Understanding_Module.LIWCdict(currentpath)

    TOKEN = token
    client = discord.Client()

    #An event that makes the bot send messages
    @client.event
    async def on_message(message):
        nonlocal currentpath, chatbot, topics, currenttopic, name, firsttime, legend, templates, clarificationasked, artistmentioned, spellnl, \
            spellname, spellartist, nlnlp, liwcdict, liwcdictnodiacritics, participantnumber, chatid, condition, lowerbound, upperbound, token
        # we do not want the bot to reply to itself
        if message.author == client.user:
            return
        # And we want to ignore messages from other channels
        if message.channel.id != chatid:
            return
        if (message.content == 'chat=start') and (chatbot == 'n'):
            chatbot = 'y'
            #msg = 'Hello {0.author.mention}'.format(message)
            msg = 'Chatbot opgestart. Berichten worden verwijderd en het gesprek begint over 10 seconden.'
            await message.delete()
            await message.channel.send(msg, delete_after=0)
            time.sleep(10)
            # For introduction we just have one question and category: Introduction (question). Get the index where the templates are
            idx = legend.index('Introduction (question)')
            # Select a random template from the list
            selectedtemplate = random.choice(templates[idx])
            # Now let's fill the template up
            filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
            #And send the message
            await message.channel.send(filledtemplate)
        elif (message.content != 'chat=start') and (message.content != 'chat=end') and (chatbot == 'n'):
            await message.channel.send('Onbekend startcommando. Berichten worden verwijderd over 5 seconden.')
            time.sleep(5)
            async for msg in message.channel.history():
                await msg.delete()
        elif message.content == 'chat=end':
            await message.channel.send('Het gesprek wordt opgeslagen. Berichten worden verwijderd over 5 seconden.')
            chatbot = 'n'
            currenttopic = 0
            name = ''
            firsttime = ''
            clarificationasked = 'n'
            artistmentioned = 'n'
            conversationlist = []
            if participantnumber == '':
                participantnumber = Answer_Understanding_Module.GetParticipantNumber(lowerbound, upperbound)

            time.sleep(5)
            async for msg in message.channel.history():
                createtime = "{0.created_at}".format(msg)
                newcreatetime = Answer_Understanding_Module.getdatetime(createtime)
                conversationlist.insert(0, newcreatetime + " : {0.author.name} : {0.content}".format(msg))
                await msg.delete()

            today = date.today()
            # dd/mm/YYYY
            d1 = today.strftime("%d-%m-%Y")
            conversationlist.insert(0, 'Date: ' + d1)
            conversationlist.insert(1, 'Chat: ' + str(message.channel.name))
            conversationlist.insert(2, 'Participant number: ' + str(participantnumber))
            conversationlist.insert(2, 'Condition: ' + str(condition))
            conversationstring = '\n'.join(conversationlist)

            with open(currentpath + '/Conversations/Pnumber_' + str(participantnumber) + '_condition_' + str(condition) + '.txt', 'wb') as f:
                f.write(bytes(conversationstring, 'UTF-8'))


        elif message.content == 'chat=kill':
            await message.channel.send('De chatbot wordt afgesloten en het gesprek wordt opgeslagen. Berichten worden verwijderd over 5 seconden.')
            chatbot = 'n'
            currenttopic = 0
            name = ''
            firsttime = ''
            clarificationasked = 'n'
            artistmentioned = 'n'
            conversationlist = []
            if participantnumber == '':
                participantnumber = Answer_Understanding_Module.GetParticipantNumber(lowerbound, upperbound)

            time.sleep(5)
            async for msg in message.channel.history():
                conversationlist.insert(0, "{0.created_at} : {0.author.name} : {0.content}".format(msg))
                await msg.delete()

            today = date.today()
            # dd-mm-YYYY
            d1 = today.strftime("%d-%m-%Y")
            conversationlist.insert(0, 'Date: ' + d1)
            conversationlist.insert(1, 'Chat: ' + str(message.channel.name))
            conversationlist.insert(2, 'Participant number: ' + str(participantnumber))
            conversationlist.insert(3, 'Condition: ' + str(condition))
            conversationlist.insert(4, '')
            conversationstring = '\n'.join(conversationlist)

            with open(currentpath + '/Conversations/Pnumber_' + str(participantnumber) + '_condition_' + str(condition) + '.txt', 'wb') as f:
                f.write(bytes(conversationstring, 'UTF-8'))

            print('Logged out as')
            print(client.user.name)
            print(client.user.id)
            print('------')
            await client.logout()

        else:
            if chatbot == 'y':
                if topics[currenttopic] == 'IntroductionResponse':
                    #Extract the name out of the message
                    name = Answer_Understanding_Module.FindName(message.content, spellname, nlnlp)
                    # If no name could be found
                    if (name == None) and (clarificationasked == 'n'):
                        # Get the template for repeat question, and ask that
                        idx = legend.index('Introduction (repeat question)')
                        # Select a random template from the list
                        selectedtemplate = random.choice(templates[idx])
                        # Now let's fill the template up
                        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
                        # And send the message
                        time.sleep(2)
                        await message.channel.send(filledtemplate)
                        #And make sure that we won't ask for clarification again
                        clarificationasked = 'y'
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
                        await message.channel.send(filledtemplate)
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
                        await message.channel.send(filledtemplate)
                        # Reset the clarificationasked
                        clarificationasked = 'n'
                        # And move onto the next topic
                        currenttopic += 1

                elif topics[currenttopic] == 'PreviousLowlandsResponse':
                    # Extract the name out of the message
                    firsttime = Answer_Understanding_Module.FindPrevious(message.content, spellnl, nlnlp)
                    # If no answer to the previous Lowlands could be found
                    if (firsttime == None) and (clarificationasked == 'n'):
                        # Get the template for repeat question, and ask that
                        idx = legend.index('Previous Lowlands (repeat question)')
                        # Select a random template from the list
                        selectedtemplate = random.choice(templates[idx])
                        # Now let's fill the template up
                        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
                        # And send the message
                        await message.channel.send(filledtemplate)
                        # And make sure that we won't ask for clarification again
                        clarificationasked = 'y'
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
                        await message.channel.send(filledtemplate)
                        # Reset the clarificationasked
                        clarificationasked = 'n'
                        # And move onto the next topic
                        currenttopic += 1

                elif topics[currenttopic] == 'LowlandsOpinionResponse':
                    #Extract the sentiment out of the message
                    opinion = Answer_Understanding_Module.FindOpinion(message.content, spellnl, nlnlp)
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
                    await message.channel.send(filledtemplate)
                    # Now move onto the next question
                    time.sleep(2)
                    # Now ask the next question about the artists on the festival
                    idx = legend.index('Artist Talk (question)')
                    # Select a random template from the list
                    selectedtemplate = random.choice(templates[idx])
                    # Now let's fill the template up
                    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
                    # And send the message
                    await message.channel.send(filledtemplate)
                    # Reset the clarificationasked
                    clarificationasked = 'n'
                    # And move onto the next topic
                    currenttopic += 1

                elif topics[currenttopic] == 'ArtistTalkResponse':
                    #Extract the artist out of the message
                    artist, domain = Answer_Understanding_Module.FindArtist(message.content, spellartist, nlnlp, artistlist, writerlist, movielist, otherlist, artistdict, writerdict, moviedict, otherdict)
                    # If no artist could be found
                    if (artist == None) and (clarificationasked == 'n'):
                        # Get the template for repeat question, and ask that
                        idx = legend.index('Artist Talk (repeat question)')
                        # Select a random template from the list
                        selectedtemplate = random.choice(templates[idx])
                        # Now let's fill the template up
                        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
                        # And send the message
                        await message.channel.send(filledtemplate)
                        #And make sure that we won't ask for clarification again
                        clarificationasked = 'y'
                        artistmentioned = 'n'
                    # If the participant still could not give an artist from the line up after the repetition, assume that they're refusing to answer
                    else:
                        if ((artist == None) and (clarificationasked == 'y')) or (artist == 'refuseArtist'):
                            artistmentioned = 'n'
                            # Find the templates
                            idx = legend.index('Artist Talk (not found)')
                            # Select a random template from the list
                            selectedtemplate = random.choice(templates[idx])
                            # Now let's fill the template up
                            filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
                            # And send the message
                            await message.channel.send(filledtemplate)
                            # Reset the clarificationasked
                            clarificationasked = 'n'
                            # And move onto the next topic
                            currenttopic += 1
                            # And take a break because we skip the opinion question
                            time.sleep(2)
                            # Now ask the next question about the artists on the festival
                            idx = legend.index('Secret (question)')
                            # Select a random template from the list
                            selectedtemplate = random.choice(templates[idx])
                            # Now let's fill the template up
                            filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, name=name)
                            # And send the message
                            await message.channel.send(filledtemplate)
                            # Reset the clarificationasked
                            clarificationasked = 'n'
                            # And move onto the next topic
                            currenttopic += 1
                        #If the participant gave a viable artist
                        else:
                            artistmentioned = 'y'
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
                                # If there are shows associated with the act, make it possible to also choose the category that talks about shows
                                if show != None:
                                    # Find the templates
                                    idx = legend.index('Artist Talk (other response; with info)')
                                    # Select a random template from the list
                                    selectedtemplateshow = random.choice(templates[idx])
                                    # Add the selected template to the selected no info template
                                    alltemplates = [selectedtemplate] + [selectedtemplateshow]
                                    # Select one of these two randomly
                                    newselectedtemplate = random.choice(alltemplates)
                                    # And fill 'er up
                                    filledtemplate, gapfiller = TemplateReplacement(newselectedtemplate, artist=artist, genre=genre, show=show)
                                else:
                                    # If there was no show associated with the act, just use the show and domain as info for the template
                                    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, artist=artist, genre=genre)
                            # And send the message
                            await message.channel.send(filledtemplate)
                            # Reset the clarificationasked
                            clarificationasked = 'n'
                            # And move onto the next topic
                            currenttopic += 1

                elif topics[currenttopic] == 'ArtistTalkOpinionResponse':
                    if artistmentioned == 'y':
                        #Extract the sentiment out of the message
                        opinion = Answer_Understanding_Module.FindOpinion(message.content, spellnl, nlnlp)
                        # If the sentiment analysis says the response is positive
                        if opinion == 'Positive':
                            # Get the template for positive response, and use that
                            idx = legend.index('Artist Talk (positive answer)')
                        # If the sentiment analysis says the response is negative
                        elif opinion == 'Negative':
                            # Find the templates
                            idx = legend.index('Artist Talk (negative answer)')
                        #If the sentiment analysis says the response is neutral
                        else:
                            # Find the templates
                            idx = legend.index('Artist Talk (no clear sentiment)')
                        # Select a random template from the list
                        selectedtemplate = random.choice(templates[idx])
                        # Now let's fill the template up
                        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
                        # And send the message
                        await message.channel.send(filledtemplate)
                        # Now move onto the next question
                        time.sleep(2)
                        # Now ask the next question about the artists on the festival
                        idx = legend.index('Secret (question)')
                        # Select a random template from the list
                        selectedtemplate = random.choice(templates[idx])
                        # Now let's fill the template up
                        filledtemplate, gapfiller = TemplateReplacement(selectedtemplate, name=name)
                        # And send the message
                        await message.channel.send(filledtemplate)
                        # Reset the clarificationasked
                        clarificationasked = 'n'
                        # And move onto the next topic
                        currenttopic += 1

                elif topics[currenttopic] == 'SecretTopicResponse':
                    # Extract the LIWC category out of the message
                    category = Answer_Understanding_Module.LIWCFeatures(message.content, liwcdict, liwcdictnodiacritics, spellnl, nlnlp)
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
                    await message.channel.send(filledtemplate)
                    # Reset the clarificationasked
                    clarificationasked = 'n'
                    # And move onto the next topic
                    currenttopic += 1

                elif topics[currenttopic] == 'SecretTopicEmotionResponse':
                    if condition == '1':
                        emotioncategory = Answer_Understanding_Module.LIWCFeatures(message.content, liwcdict, liwcdictnodiacritics, spellnl, nlnlp, 'y')
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
                    await message.channel.send(filledtemplate)
                    # Reset the clarificationasked
                    clarificationasked = 'n'
                    # And move onto the next topic
                    currenttopic += 1

                elif topics[currenttopic] == 'EndofConversation':
                    # End the conversation
                    idx = legend.index('Goodbye')
                    # Select a random template from the list
                    selectedtemplate = random.choice(templates[idx])
                    # Now let's fill the template up
                    filledtemplate, gapfiller = TemplateReplacement(selectedtemplate)
                    # And send the message
                    await message.channel.send(filledtemplate)
                    #Wait for a bit
                    time.sleep(2)
                    #Get a participant number
                    participantnumber = Answer_Understanding_Module.GetParticipantNumber(lowerbound, upperbound)
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
                    await message.channel.send(filledtemplate)
                    # Reset the clarificationasked
                    clarificationasked = 'n'
                    # And move onto the next topic
                    currenttopic += 1

                elif topics[currenttopic] == 'IdleChat':
                    await message.channel.send('Ongeldig eindcommando')

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    client.run(TOKEN)

replymessage()