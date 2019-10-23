import os
import random
import time
import regex as re
import sys
import requests
import json
import sqlite3
import operator
from pattern.nl import sentiment, lemma, predicative, singularize, conjugate, PRESENT, SG, attributive
import csv
from unidecode import unidecode
from datetime import date, datetime, timedelta
import Participant_Number_Module

def GetParticipantNumber(lowerbound, upperbound):
    # Get a new participantnumber
    for num in range(lowerbound, upperbound):
        #If there is no database yet, just return the first number
        if not os.path.exists(os.getcwd() + '/Databases/ParticipantNumbers.db'):
            #Save the participant number
            Participant_Number_Module.database_main(os.getcwd() + '/Databases/ParticipantNumbers.db', num)
            #And return the number
            return str(num)
        #Search until the first number that is not in the list is found
        elif Participant_Number_Module.database_search(os.getcwd() + '/Databases/ParticipantNumbers.db', num) == 'notFound':
            # Save the participant number
            Participant_Number_Module.database_main(os.getcwd() + '/Databases/ParticipantNumbers.db', num)
            #And return the number
            return str(num)

def getdatetime(datestring):
    #Get the date as e.g. 22-04-2019
    #Get the time as 14:39:11
    timetemplate = '%H:%M:%S'
    #Original timestring is like 2019-04-07T12:39:11.422Z, so let's remove the milliseconds first (the stuff after the period)
    datestring = re.search(r'^(.*?) (.*?)\.', datestring).group(2)
    #Convert the string to a datetime object
    datetime_obj = datetime.strptime(datestring, "%H:%M:%S")  + timedelta(hours=2)
    #Return a tuple with a datestring and a timestring
    return datetime_obj.strftime(timetemplate)

def generate_ngrams(s, n):
    # Convert to lowercases
    s = s.lower()

    # Replace all none alphanumeric characters with spaces
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)

    # Break sentence in the token, remove empty tokens
    tokens = [token for token in s.split(" ") if token != ""]

    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]

def wordtokenizer(message, nlnlp):
    nldoc = nlnlp(message)
    # Return the lowercase token if the token is not actually punctuation
    tokenlist = [token.text.lower() for token in nldoc if re.search(r"^\p{P}+$", token.text) == None]
    return tokenlist

def wordvarieties(word):
    lem = lemma(word)
    pre = predicative(word)
    att = attributive(word)
    sin = singularize(word)
    con = conjugate(word, PRESENT, 1, SG)
    return [lem, pre, att, sin, con]

def database_search_names(db, searchword):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        while True:
            try:
                cur.execute("SELECT * FROM firstnames WHERE firstname = ? COLLATE NOCASE", (searchword,))
                break
            except sqlite3.OperationalError:
                time.sleep(1)

        data = cur.fetchone()
        if data is None:
            return 'notFound'
        else:
            return data[0]

def FindName(message, spellname, nlnlp):
    #Words people may use in front of their name when introducing themselves
    prenamelist = ['ik ben', 'naam is', 'ik heet', 'noemen mij', 'noem mij']
    #Words people may use after their name when introducing themselves
    postnamelist = ['ben ik', 'is de naam', 'heet ik', 'noemen ze mij', 'word ik genoemd']
    #They may refuse using probably the word 'niet' in combination with one of the other words in the list
    refuselist = ['vertellen', 'zeggen', 'voorstellen', 'geven', 'vertel', 'zeg', 'stel', 'geef', 'beantwoorden', 'beantwoord', 'antwoorden', 'antwoord']

    prenamefound = False
    postnamefound = False
    refusenamefound = False
    name = None
    #First we try to see if there is one of the pre-name constructions in the message
    for prename in prenamelist:
        if re.search(r'^(.*?)\b%s\b' % prename, message, re.IGNORECASE):
            examplenamefound = False
            #If so, delete the pre-name construction and punctuation from the message
            name = re.sub(r'^(.*?)\b%s\b' % prename, '', message, flags=re.IGNORECASE)
            name = re.sub(r'\p{P}+', '', name, flags=re.IGNORECASE)
            name = name.strip()
            #And check if we can find the name in the list of first names
            #Split the remaining string into words
            tokenlist = wordtokenizer(name, nlnlp)
            #And search for every word if there's a match in the name database
            for word in tokenlist:
                namefind = database_search_names(os.getcwd() + '/Databases/voornamen.db', word)
                if namefind != 'notFound':
                    name = namefind
                    examplenamefound = True
                    break

            #If we cannot find the name in the list, there might be a typo in there.
            if examplenamefound == False:
                #Use a spellcheck trained on the list of first names
                tokenlist = [spellname.correction(x) for x in tokenlist]
                #And check if we can find the name in the list of first names now
                for word in tokenlist:
                    namefind = database_search_names(os.getcwd() + '/Databases/voornamen.db', word)
                    if namefind != 'notFound':
                        name = namefind
                        break
            #Otherwise, we will just assume that the part after the pre-name construction is the name
            prenamefound = True
            break

    #If we couldn't find the name with a pre-name construction, we will check the post-name constructions.
    if prenamefound == False:
        for postname in postnamelist:
            if re.search(r'\b%s\b(.*?)$' % postname, message, re.IGNORECASE):
                examplenamefound = False
                #If the post-name construction is found, delete the post-name constuction and punctuation from the message
                name = re.sub(r'\b%s\b(.*?)$' % postname, '', message, flags=re.IGNORECASE)
                name = re.sub(r'\p{P}+', '', name, flags=re.IGNORECASE)
                name = name.strip()
                # And check if we can find the name in the list of first names
                # Split the remaining string into words
                tokenlist = wordtokenizer(name, nlnlp)
                # And search for every word if there's a match in the name database
                for word in tokenlist:
                    namefind = database_search_names(os.getcwd() + '/Databases/voornamen.db', word)
                    if namefind != 'notFound':
                        name = namefind
                        examplenamefound = True
                        break

                # If we cannot find the name in the list, there might be a typo in there.
                if examplenamefound == False:
                    # Use a spellcheck trained on the list of first names
                    tokenlist = [spellname.correction(x) for x in tokenlist]
                    # And check if we can find the name in the list of first names now
                    for word in tokenlist:
                        namefind = database_search_names(os.getcwd() + '/Databases/voornamen.db', word)
                        if namefind != 'notFound':
                            name = namefind
                            break
                postnamefound = True
                break

    #If we couldn't find the prename or postname construction, we'll check if the participant refused to answer.
    if (prenamefound == False) and (postnamefound == False):
        for refuse in refuselist:
            if ((re.search(r'\b%s\b' % refuse, message.lower())) and (re.search(r"\bniet\b", message.lower()))) or (
                    re.search(r"\bgeheim\b", message.lower())) or ((re.search(r'\b%s\b' % refuse, message.lower())) and (re.search(r"\bweiger\b", message.lower()))) or (
                    re.search(r"\b((niets)|(niks)) aan\b", message.lower())) or (message.lower() == '') or (not re.search(r'[a-zA-Z]', message.lower())):
                refusenamefound = True
                name = 'refuseName'
                break
        #If we can't find the refuse words, we'll check again with the spellchecker
        if refusenamefound == False:
            tokenlist = wordtokenizer(message, nlnlp)
            tokenlist = [spellname.correction(x) for x in tokenlist]
            newmessage = ' '.join(tokenlist)
            for refuse in refuselist:
                if ((re.search(r'\b%s\b' % refuse, newmessage)) and (re.search(r"\bniet\b", newmessage))) or (
                    re.search(r"\bgeheim\b", newmessage)) or ((re.search(r'\b%s\b' % refuse, newmessage)) and (re.search(r"\bweiger\b", newmessage))) or (
                    re.search(r"\b((niets)|(niks)) aan\b", newmessage)) or (not re.search(r'[a-zA-Z]', newmessage)):
                    refusenamefound = True
                    name = 'refuseName'
                    break

    #If we still haven't found the name, we can check if we can find the first name in the message itself
    if (prenamefound == False) and (postnamefound == False) and (refusenamefound == False):
        examplenamefound = False
        # Split the remaining string into words
        tokenlist = wordtokenizer(message, nlnlp)
        # And search for every word if there's a match in the name database
        for word in tokenlist:
            namefind = database_search_names(os.getcwd() + '/Databases/voornamen.db', word)
            if namefind != 'notFound':
                name = namefind
                examplenamefound = True
                break
        #If the name wasn't found the first time, use the spell corrector to see if that returns the first name
        if examplenamefound == False:
            tokenlist = [spellname.correction(x) for x in tokenlist]
            for word in tokenlist:
                namefind = database_search_names(os.getcwd() + '/Databases/voornamen.db', word)
                if namefind != 'notFound':
                    name = namefind
                    break

    #If all other methods haven'' returned the name and if the message is 4 words or less, and more than 1 word,
    #The chat message might just be the name
    if (name == None) and (prenamefound == False) and (postnamefound == False) and (refusenamefound == False) and (
            len(message.split()) > 0) and (len(message.split()) <= 4):
        name = message.title()

    return name

def FindPrevious(message, spellnl, nlnlp):
    tokenlist = wordtokenizer(message, nlnlp)
    tokenlist = [spellnl.correction(x) for x in tokenlist]
    message = ' '.join(tokenlist)
    #List of words that confirm they've been to Lowlands before
    confirmationwords = ['ja', 'jep', 'jup', 'yes', 'jawel', 'zeker', 'zekers', 'allicht', 'oui', 'si', 'inderdaad', 'juist', 'klopt', 'precies',
                         'positief', 'uhu', 'jawohl', 'vaker', 'eerder', 'uiteraard', 'tuurlijk', 'jazeker', 'heel vaak', 'te vaak']
    #Words that negate that they've been to Lowlands before
    negationwords = ['nee', 'nope', 'nah', 'no', 'nein', 'negatief', 'nooit', 'niet', 'non', 'neen', 'eerste', '1', '1e', '1ste']
    #Words that would indicate the amount of times they've been to Lowlands before or the years they've been to Lowlands before
    countwords = ['tweede', 'derde', 'vierde', 'vijfde', 'zesde', 'zevende', 'achtste', 'negende', 'tiende', 'elfde', 'twaalfde', 'dertiende',
                  'veertiende', 'vijftiende', 'zestiende', 'zeventiende', 'achtiende', 'negentiende', 'twintigste', 'eenentwintigste', 'tweeëntwintigste',
                  'tweeentwintigste', 'drieëntwintigste', 'drieentwintigste', 'vierentwintigste', 'vijfentwintigste', 'zesentwintigste', 'zevenentwintigste',
                  'twee', 'drie', 'vier', 'vijf', 'zes', 'zeven', 'acht', 'negen', 'tien', 'elf', 'twaalf', 'dertien', 'veertien', 'vijftien', 'zestien',
                  'zeventien', 'achtien', 'negentien', 'twintig', 'eenentwintig', 'tweeëntwintig', 'tweeentwintig', 'drieëntwintig', 'drieentwintig',
                  'vierentwintig', 'vijfentwintig', '00', "'00", '01', "'01", '2', '2e', '2de', '02', "'02", '3', '3e', '3de', '03', "'03", '4', '4e', '4de', '04', "'04", '5',
                  '5e', '5de', '05', "'05", '6', '6e', '6de', '06', "'06", '7', '7e', '7de', '07', "'07", '8', '8e', '8ste', '08', "'08", '9', '9e',
                  '9de', '09', "'09", '10', '10e', '10de', "'10", '11', '11e', '11de', "'11", '12', '12e', '12de', "'12", '13', '13e', '13de', "'13",
                  '14', '14e', '14de', "'14", '15', '15e', '15de', "'15", '16', '16e', '16de', "'16", '17', '17e', '17de', "'17", '18', '18e', '18de',
                  "'18", '19', '19e', '19de', "'19", '20', '20e', '20ste', '21', '21e', '21ste', '22', '22e', '22ste', '23', '23e', '23ste', '24',
                  '24e', '24ste', '25', '25e', '25ste', '26', '26e', '26ste', '27', '27e', '27ste', '67', "'67", '68', "'68", '93', "'93", '94', "'94",
                  '95', "'95", '96', "'96", '97', "'97", '98', "'98", '99', "'99", '1967', '1968', '1993', '1994', '1995', '1996', '1997', '1998',
                  '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014',
                  '2015', '2016', '2017', '2018', 'tig', 'heleboel', 'zoveel', 'zoveelste', 'ontelbaar']

    refuselist = ['vertellen', 'zeggen', 'geven', 'vertel', 'zeg', 'geef', 'beantwoord', 'beantwoorden', 'antwoord', 'antwoorden']
    for refuse in refuselist:
        if ((re.search(r'\b%s\b' % refuse, message)) and (re.search(r"\bniet\b", message))) or (
                re.search(r"\bgeheim\b", message)) or ((re.search(r'\b%s\b' % refuse, message)) and (re.search(r"\bweiger\b", message))) or (
                re.search(r"\b((niets)|(niks)) aan\b", message)) or (not re.search(r'[a-zA-Z]', message)):
            return 'RefuseTime'
    #If there's a negation in there, we assume it's the first time
    for negate in negationwords:
        if re.search(r'\b%s\b(.*?)$' % negate, message):
            return 'FirstTime'
    #If there's a confirmation in there, we assume it's not the first time
    for confirm in confirmationwords:
        if re.search(r'\b%s\b(.*?)$' % confirm, message):
            return 'BeenBefore'
    #If there's a word relating to counting or a year in there, we assume it's not the first time
    for count in countwords:
        if re.search(r'\b%s\b(.*?)$' % count, message):
            return 'BeenBefore'
    #If we didn't find anything related to previous experiences, return None
    return None

def FindOpinion(message, spellnl, nlnlp):
    tokenlist = wordtokenizer(message, nlnlp)
    tokenlist = [spellnl.correction(x) for x in tokenlist]
    message = ' '.join(tokenlist)
    sentimenttuple = sentiment(message)
    compoundsentiment = sentimenttuple[0]
    if compoundsentiment > 0.3:
        return 'Positive'
    elif compoundsentiment < -0.3:
        return 'Negative'
    else:
        return 'Neutral'

def FindArtist(message, spellartist, nlnlp, artistlist, writerlist, movielist, otherlist, artistdict, writerdict, moviedict, otherdict):
    # They may refuse using probably the word 'niet' in combination with one of the other words in the list
    refuselist = ['vertellen', 'zeggen', 'geven', 'vertel', 'zeg', 'geef', 'beantwoord', 'beantwoorden', 'antwoord', 'antwoorden', 'niets', 'niks']
    nothinglist = ['niets', 'niks', 'geen', 'noppes', 'nada', 'niet', 'nul', 'zero']
    #Shuffle the artistlist, so that we don't pick the same artist all the time to respond to in cases where multiple artists are mentioned
    random.shuffle(artistlist)
    #And do the same for the other lists
    random.shuffle(writerlist)
    random.shuffle(movielist)
    random.shuffle(otherlist)

    #Make a list containing all the stuff
    alllist = {'music': artistlist, 'books': writerlist, 'movies': movielist, 'other': otherlist}
    alldict = [artistdict, writerdict, moviedict, otherdict]

    #Go over the domains (fixed order since most people will go for an artist and this order would probably provide the answer the quickest.
    for idx, domain in enumerate(alllist):
        for artist in alllist[domain]:
            #Delete punctuation from the artist name
            #artist = re.sub(r"\p{P}+", '', artist)
            #And see if we can find the artist in the message
            if (re.search(r'\b%s\b' % artist.lower(), message.lower())):
                return artist, domain

            #For the longer names, let's just see if we can find a bigram in the message
            bigrams = generate_ngrams(artist, 2)
            for bigram in bigrams:
                if (re.search(r'\b%s\b' % bigram.lower(), message.lower())):
                    return artist, domain

            #Else, search if one of the unique artist words can be found in the sentence
            for uniqueword in alldict[idx][artist]:
                if (re.search(r'\b%s\b' % uniqueword.lower(), message.lower())):
                    return artist, domain


    for refuse in refuselist:
        if ((re.search(r'\b%s\b' % refuse, message.lower())) and (re.search(r"\bniet\b", message.lower()))) or (
                re.search(r"\bgeheim\b", message.lower())) or ((re.search(r'\b%s\b' % refuse, message.lower())) and (re.search(r"\bweiger\b", message.lower()))) or (
                re.search(r"\b((niets)|(niks)) aan\b", message.lower())) or (not re.search(r'[a-zA-Z]', message.lower())):
            return 'refuseArtist', 'refuseArtist'
    for nothing in nothinglist:
        if re.search(r'\b%s\b' % nothing, message.lower()):
            return 'refuseArtist', 'refuseArtist'

    #If no artist could be found, spell correct the message
    tokenlist = wordtokenizer(message, nlnlp)
    tokenlist = [spellartist.correction(x) for x in tokenlist]
    message = ' '.join(tokenlist)

    #And try to find an artist again
    for idx, domain in enumerate(alllist):
        for artist in alllist[domain]:
            # Delete punctuation from the artist name
            # artist = re.sub(r"\p{P}+", '', artist)
            # And see if we can find the artist in the message
            if (re.search(r'\b%s\b' % artist.lower(), message.lower())):
                return artist, domain

            # For the longer names, let's just see if we can find a bigram in the message
            bigrams = generate_ngrams(artist, 2)
            for bigram in bigrams:
                if (re.search(r'\b%s\b' % bigram.lower(), message.lower())):
                    return artist, domain

            # Else, search if one of the unique artist words can be found in the sentence
            for uniqueword in alldict[idx][artist]:
                if (re.search(r'\b%s\b' % uniqueword.lower(), message.lower())):
                    return artist, domain


    for refuse in refuselist:
        if ((re.search(r'\b%s\b' % refuse, message.lower())) and (re.search(r"\bniet\b", message.lower()))) or (
                re.search(r"\bgeheim\b", message.lower())) or ((re.search(r'\b%s\b' % refuse, message.lower())) and (re.search(r"\bweiger\b", message.lower()))) or (
                re.search(r"\b((niets)|(niks)) aan\b", message.lower())) or (not re.search(r'[a-zA-Z]', message.lower())):
            return 'refuseArtist', 'refuseArtist'

    #If no artist could be found, return None
    return 'refuseArtist', 'refuseArtist'

def artist_search(db, searchword):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        while True:
            try:
                cur.execute("SELECT * FROM artists WHERE artist = ?", (searchword,))
                break
            except sqlite3.OperationalError:
                time.sleep(1)
        data = cur.fetchone()
        if data is None:
            return 'notFound'
        else:
            albums = list(data[1:11])
            albums = [x for x in albums if x != '']
            tracks = list(data[11:21])
            tracks = [x for x in tracks if x != '']
            genres = list(data[21:31])
            genres = [x for x in genres if x != '']
            album = random.choice(albums)
            track = random.choice(tracks)
            genre = genres[0]
            return album, track, genre

def movie_search(db, searchword):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        while True:
            try:
                cur.execute("SELECT * FROM movies WHERE movie = ?", (searchword,))
                break
            except sqlite3.OperationalError:
                time.sleep(1)
        data = cur.fetchone()
        if data is None:
            return 'notFound'
        else:
            actors = list(data[1:6])
            actors = [x for x in actors if x != '']
            genres = list(data[6:11])
            genres = [x for x in genres if x != '']
            directors = list(data[11:16])
            directors = [x for x in directors if x != '']
            actor = random.choice(actors)
            genre = genres[0]
            director = directors[0]
            return actor, genre, director

def writer_search(db, searchword):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        while True:
            try:
                cur.execute("SELECT * FROM writers WHERE writer = ?", (searchword,))
                break
            except sqlite3.OperationalError:
                time.sleep(1)
        data = cur.fetchone()
        if data is None:
            return 'notFound'
        else:
            books = list(data[1:11])
            books = [x for x in books if x != '']
            book = random.choice(books)
            return book

def other_search(db, searchword):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        while True:
            try:
                cur.execute("SELECT * FROM other WHERE artist = ?", (searchword,))
                break
            except sqlite3.OperationalError:
                time.sleep(1)
        data = cur.fetchone()
        if data is None:
            return 'notFound'
        else:
            domain = data[1]
            shows = list(data[2:12])
            shows = [x for x in shows if x != '']
            if len(shows) == 0:
                show = None
            else:
                show = random.choice(shows)
            return domain, show

def LIWCdict(currentpath):
    liwcdict = {}

    with open(currentpath + '/Databases/' + 'LIWC_FILE', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')

        for idx, row in enumerate(reader):
            if idx > 0:
                newrow = list(filter(None, row))
                liwcdict.update({newrow[0]: newrow[1:]})

    liwcdictnodiacritics = {unidecode(k): v for k, v in liwcdict.items()}
    return liwcdict, liwcdictnodiacritics

def LIWCFeatures(message, liwcdict, liwcdictnodiacritics, spellnl, nlnlp, onlyemotions='n'):
    tokenlist = wordtokenizer(message, nlnlp)
    tokenlist = [spellnl.correction(x) for x in tokenlist]
    liwctotals = {}
    #Check if the regular word is in LIWC
    for idx, word in enumerate(tokenlist):
        word = spellnl.correction(word)
        liwcvalue = None
        if word in liwcdict:
            liwcvalue = liwcdict[word]
        #Key is not present
        elif word in liwcdictnodiacritics:
            #Check if people maybe use the word without diacritics (e.g. beinvloeden instead of beïnvloeden)
            liwcvalue = liwcdictnodiacritics[word]
        else:
            #Get the variants of the word
            varietylist = wordvarieties(word)
            #Check if the variety is in LIWC
            for variety in varietylist:
                if variety in liwcdict:
                    liwcvalue = liwcdict[variety]
                    break
                elif variety in liwcdictnodiacritics:
                    liwcvalue = liwcdict[variety]
                    break
        #Add the liwccategories associated with the word to the liwcdict
        if liwcvalue != None:
            for value in liwcvalue:
                newvalue = 'liwc' + str(value)
                if newvalue not in liwctotals:
                    liwctotals[newvalue] = 1
                else:
                    liwctotals[newvalue] += 1

    #Get the liwcscores connected to the relevant categories for secrets
    selectliwctotals = {}
    if onlyemotions == 'n':
        for key in liwctotals:
            if (key == 'liwc30') or (key == 'liwc31') or (key == 'liwc32') or (key == 'liwc33') or (key == 'liwc34') or (key == 'liwc35')\
                    or (key == 'liwc40') or (key == 'liwc41') or (key == 'liwc42') or (key == 'liwc43') or (key == 'liwc44') or (key == 'liwc71') \
                    or (key == 'liwc72') or (key == 'liwc73') or (key == 'liwc74') or (key == 'liwc81') or (key == 'liwc82') or (key == 'liwc83')\
                    or (key == 'liwc84') or (key == 'liwc85') or (key == 'liwc110') or (key == 'liwc111') or (key == 'liwc112') or (key == 'liwc113') \
                    or (key == 'liwc114') or (key == 'liwc115') or (key == 'liwc121'):
                selectliwctotals.update({key: liwctotals[key]})
    #If you want the emotion categories only, get the scores on these categories
    else:
        for key in liwctotals:
            if (key == 'liwc31') or (key == 'liwc32') or (key == 'liwc33') or (key == 'liwc34') or (key == 'liwc35'):
                selectliwctotals.update({key: liwctotals[key]})

    #If no emotions are found, use the opinion function to find the sentiment and use that to say if something is positive or negative emotion
    if selectliwctotals == {}:
        opinion = FindOpinion(message, spellnl, nlnlp)
        if opinion == 'Positive':
            selectliwctotals.update({'liwc31': 1})
        elif opinion == 'Negative':
            selectliwctotals.update({'liwc32': 1})

    if selectliwctotals == {}:
        return 'noLIWC'
    else:
        #Remove the more vague categories and see if there are still some categories left
        selectliwctotals2 = {i: selectliwctotals[i] for i in selectliwctotals if (i != 'liwc30') and (i != 'liwc40') and (i != 'liwc41') and (i != 'liwc42') and (i != 'liwc81')}
        #If there's still one or more categories left, find out which one is the most frequent in the secret told and return that one, otherwise return one of the vague categories
        if selectliwctotals2 != {}:
            return max(selectliwctotals2.items(), key=operator.itemgetter(1))[0]
        else:
            return max(selectliwctotals.items(), key=operator.itemgetter(1))[0]