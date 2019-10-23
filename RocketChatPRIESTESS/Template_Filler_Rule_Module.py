from datetime import datetime

def templatefillers(gap, **kwargs):
    if gap == 'daytime':
        present = datetime.now()
        if present.hour <= 11:
            return 'morning'
        if present.hour > 16:
            return 'evening'
        else:
            return 'afternoon'
    elif gap == 'name':
        return kwargs['name']
    elif gap == 'spacename':
        if (kwargs['name'] == None) or (kwargs['name'] == 'refuseName') or (kwargs['name'] == ''):
            return ''
        else:
            return ' ' + kwargs['name']
    elif gap == 'city':
        return kwargs['city']
    elif gap == 'distance':
        return kwargs['distance']
    elif gap == 'artist':
        return kwargs['artist']
    elif gap == 'song':
        return kwargs['song']
    elif gap == 'genre':
        return kwargs['genre']
    elif gap == 'album':
        return kwargs['album']
    elif gap == 'director':
        return kwargs['director']
    elif gap == 'actor':
        return kwargs['actor']
    elif gap == 'book':
        return kwargs['book']
    elif gap == 'show':
        return kwargs['show']
    elif (gap == 'emotion') or (gap == 'related') or (gap == 'genderbody') or (gap == 'drives') or (gap == 'perscon') or (gap == 'emotion'):
        liwcdict = {'liwc30': 'affect', 'liwc31': 'posemo', 'liwc32': 'negemo', 'liwc33': 'anx', 'liwc34': 'anger', 'liwc35': 'sad',
                    'liwc40': 'social', 'liwc41': 'family', 'liwc42': 'friend', 'liwc43': 'female', 'liwc44': 'male', 'liwc71': 'body',
                    'liwc72': 'health', 'liwc73': 'sexual', 'liwc74': 'ingest', 'liwc81': 'affiliation', 'liwc82': 'achieve', 'liwc83': 'power',
                    'liwc84': 'reward', 'liwc85': 'risk', 'liwc110': 'work', 'liwc111': 'leisure', 'liwc112': 'home', 'liwc113': 'money',
                    'liwc114': 'relig', 'liwc115': 'death', 'liwc121': 'swear'}
        return liwcdict[kwargs['liwccat']]
    elif gap == 'link':
        newlink = kwargs['link']
        return newlink
    else:
        print(gap)






        

