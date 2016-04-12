from TwitterAPI import TwitterAPI
import os
import re


consumer_key = ""
consumer_secret = ""
access_token_secret = ""
access_token_key = ""

def filename_matcher(text, filename):
    if text == filename:
        return True
    li = text.split()
    if filename.endswith(('.mp3','.MP3','.mp4','.m3u','.m4a','.wav','.flv')):
        filename = filename[:-4]
    fn_list = re.split(' |-|_|\.', filename.lower())
    for word in li:
        if word.lower() in fn_list:
            fn_list.pop(fn_list.index(word.lower()))
        else:
            return False
    return True

def totem(command, device, output):
    cl = 'totem ' + command['intent']
    if command['intent'] == '--play':

        for alias in device['alias']:
            command['arguments']['name'] = command['arguments']['name'].replace(alias, 'totem')

        # Remove 'totem' and 'in','with','using' if it exists in the filname
        if ('totem') in command['arguments']['name']:
            temp = command['arguments']['name'].split(' ')
            temp.remove('totem')
            if temp[len(temp)-1] in ['in','with','using']:
                del temp[len(temp)-1]
            command['arguments']['name'] = ' '.join(temp)

        #Only `totem --play` will unpause the application
        # If the name of a song is mentioned `totem --play songname` will be executed
        if command['arguments']['name']:
            command['arguments']['name'] = command['arguments']['name'].strip(' ')

            matched_files = [] # Keep track of all the files that match

            # Walk in the required directories to find music
            for dirName, subdirList, fileList in os.walk("./"):
                for filename in fileList:
                    if filename_matcher(command['arguments']['name'], filename):
                        # print('Matched: ', filename)
                        matched_files.append(filename)
            if len(matched_files) == 0:
                output['message'] = 'No files were found'
                return output
            elif len(matched_files) > 1:
                output['final'] = False
                output['message'] = 'Which song do you want to play?'
                output['options'] = matched_files
                output['type'] = 'option'
                output['option-type'] = 'arguments' # Refer JSON to know what this refers to
                output['option-name'] = 'name' # Refer JSON to know what this refers to
                return output
            else:
                output = {
                    'commands': [],
                    'error': False,
                    'final': True,
                    'parsed': command,
                    'message': 'Executed command',
                    'type': None,
                }
                cl += ' "' + matched_files[0] + '"'
    cl += ' &'
    return_value = os.system(cl)
    if return_value == 0:
        return output
    # What should we do if return value isn't 0?
    return output

def tweet(command, device, output):
    tweets = []
    others = True # used to differentitae trending tweets from others

    try:
        api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
        obj = command['arguments']['name']

        if command['intent'] == 'trends/place':
            others = False
            res = api.request('trends/available') # to find the what on earth id 'an id for a particular place'
            for i in res:
                if i['country'].lower() == command['arguments']['name'][1:]:
                    woeid = i['woeid']

            response = api.request(command['intent'], {'id':woeid}) # you only get links to trending news in twitter
            count = 0 # specifies no of tweets for places 'currently  5'
            for item in response:
                count += 1
                if not re.match('[a-zA-Z0-9]',item['query'][0]):
                    ret_query = item['query'][3:]
                else:
                    ret_query = item['query']
                tweets.append(ret_query + '<br />       ' + str(item['url'])) # change the output format as required
                if count == 5:
                    break

        elif command['intent'] == 'statuses/user_timeline':
            query = 'screen_name'

        else:
            query = 'q'

        if others == True: # if the request is not on trending news
            response = api.request(command['intent'], {query:obj, 'count':5})
            print(response.status_code)

            for item in response:
                string = item['text'].replace('\n', '<br />')
                tweets.append(string)
                # print(item['text'])

        # FOR MAKING HREF LINKS
        no_of_tweets = len(tweets)
        for i in range(no_of_tweets):
            tweet_length = len(tweets[i])
            while 1:
                first_char = 0
                index = tweets[i].find('http', first_char, tweet_length)
                if index == -1:
                    break
                m = index # 'm' to find the end of https
                while tweets[i][m]!=' ' and m < (tweet_length-1):
                    m += 1
                if m < tweet_length:
                    text = tweets[i][index:m+1]
                    tweets[i] = tweets[i].replace(text, 'replace')
                    first_char = m
                    tweet_length = len(tweets[i])

            replace_index = tweets[i].find('replace')
            if replace_index != -1:
                blank = '_blank'
                replace = '<a href = '+text+' target = '+blank+'>'+text+'</a> '
                tweets[i] = tweets[i].replace('replace', replace)
                # print(tweets[i])

        output = {
             'commands': [],
             'error': False,
             'final': True,
             'parsed': command,
             'message': 'Executed command',
             'type': None,
             'tweet': tweets
        }
        return output

    except:
        output = {
           'message':'invalid input',
           'error':True,
           'final':True
        }
        return output

def process(command, device, output):
    if command['device'] == 'totem':
        return totem(command, device, output)
    if command['device'] == 'tweet':
        return tweet(command, device, output)
    if command['device'] == 'soundcloud':
        return soundcloud(command, device, output)
    elif command['device'] == 'tetris':
        return tetris(command, device, output)

def tetris(command, device, output):
    return output

def soundcloud(command, device, output):
    return output
