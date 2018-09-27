import requests
import time
import datetime

class Virgin1BotHandler:
    
    VERSION="1.3.2"
    UNDERSTANDABLE_LANGUAGE=('hello','bonjour','hi','greetings','sup')

    def __init__(self, token):
        self.token=token
        self.api_url="https://api.telegram.org/bot{}/".format(token)

    def get_updates(self,offset=None,timeout=1):
    #def get_updates(self,offset=None,timeout=30):
        method='getUpdates'
        params={'timeout':timeout,'offset':offset}
        resp=requests.get(self.api_url+method,params)
        result_json=resp.json()['result']
        return result_json

    def send_message(self,chat_id,text):
        params={'chat_id':chat_id,'text':text}
        method='sendMessage'
        resp=requests.post(self.api_url+method,params)
        return resp

    def get_last_update(self):
        get_result=self.get_updates()

        if len(get_result)>0:
            last_update=get_result[-1]
        else:
            last_update=None
            #last_update=get_result[len(get_result)]

        return last_update

# --- END CLASS DEF ---
def main():
    new_offset=None
    token=$VIRGIN1_TOKEN
    virgin1bot=Virgin1BotHandler(token)

    print("Starting bot now")

    while True:
        now=datetime.datetime.now()
        today=now.day
        hour=now.hour
        #print('inside main loop')
        virgin1bot.get_updates(new_offset)

        last_update=virgin1bot.get_last_update()

        if last_update:
            print('last_update: ',last_update)
            last_update_id=last_update['update_id']
            last_chat_id = last_update['message']['chat']['id']
            last_chat_text= last_update['message']['text']
            last_chat_name= last_update['message']['chat']['first_name']
            last_chat_epochtime=last_update['message']['date']

            print('datetime.datetime.now() is: ', now)
            print('date time hour is: ',hour)
            print('last_chat_epochtime is: ',last_chat_epochtime)
            print('converted last_chat_epochtime is: ',time.localtime(last_chat_epochtime))
            hour=time.localtime(last_chat_epochtime).tm_hour
            print('date time hour is: ',hour)

            #if last_chat_text.lower() in virgin1bot.UNDERSTANDABLE_LANGUAGE and today == now.day and 6 <= hour < 12:
            if last_chat_text.lower() in virgin1bot.UNDERSTANDABLE_LANGUAGE and 5 <= hour < 12:
                virgin1bot.send_message(last_chat_id,'Good Morning {}'.format(last_chat_name))
                #today+=1

            elif last_chat_text.lower() in virgin1bot.UNDERSTANDABLE_LANGUAGE and 12 <= hour < 17:
                virgin1bot.send_message(last_chat_id,'Good Afternoon {}'.format(last_chat_name))

            elif last_chat_text.lower() in virgin1bot.UNDERSTANDABLE_LANGUAGE and 17 <= hour <= 23:
                virgin1bot.send_message(last_chat_id,'Good Evening {}'.format(last_chat_name))

            elif last_chat_text.lower() in virgin1bot.UNDERSTANDABLE_LANGUAGE: 
                virgin1bot.send_message(last_chat_id,'It is now {} am, you should go to bed my dear {} <3'.format(hour,last_chat_name))

            else:
                virgin1bot.send_message(last_chat_id,'I\'m sorry my friend, {}.\nI am a very inexperienced virgin so I do not understand what you are trying to say...'.format(last_chat_name))

            new_offset=last_update_id+1

        #else:
            #print('nothing to see here')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
