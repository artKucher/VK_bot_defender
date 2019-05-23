import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
import json
import random

blacklistUsers = {103844138, 71446998}
MenuMessages = {'setting_mode_enable': 'NICE, SETTING MOD IS ENABLED write add to ADD new rule or EXIT to you know what',
                'setting_mode_disable': 'SETTING MOD IS DISABLED',
                'misunderstanding': 'SORRY, I DONT UNDERSTAND',
                'new_filter': 'Now forward message from chat you want to filter or EXIT to exit',
                'new_filter_send_people_link': 'Now sent vk link of person youd like to mute or EXIT',
                'ned_filter_added':'stalking him now',
                'setting_mode_error_no_forward':'PLEASE, FORWARD MESSAGE'}
MessageRules = {}
MyId = 0

def main():
    session = requests.Session()
    vk_session = vk_api.VkApi(token="HERE SHOULD BE YOUR TOKEN")

    setting_mode = False
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    MyId = vk.users.get()[0]['id']
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            #возможная команда
            if event.user_id==MyId and event.to_me:
                # вход в режим настроек
                print(vk.messages.getById(message_ids=event.message_id)["items"])
                if str(event.text)[:6].lower()=="setbot":
                    setting_mode = True
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.user_id,
                        message=MenuMessages['setting_mode_enable'],
                        random_id=str(random.randint(111111, 99999999))
                    )
                else:
                    if setting_mode and  event.text not in list(MenuMessages.values()) :
                        if str(event.text)[:4].lower()=="exit":
                            setting_mode = False
                            vk.messages.send(  # Отправляем сообщение
                                user_id=event.user_id,
                                message=MenuMessages['setting_mode_disable'],
                                random_id=str(random.randint(111111, 99999999))
                            )
                        elif str(event.text)[:2].lower()=="nf":
                            vk.messages.send(  # Отправляем сообщение
                                user_id=event.user_id,
                                message=MenuMessages['new_filter'],
                                random_id=str(random.randint(111111, 99999999))
                            )
                            nf_chat_selected = 0
                            for event_nf in longpoll.listen():
                                if event_nf.type == VkEventType.MESSAGE_NEW and str(event_nf.text)[:4].lower()=="exit":
                                    vk.messages.send(  # Отправляем сообщение
                                        user_id=event_nf.user_id,
                                        message=MenuMessages['setting_mode_enable'],
                                        random_id=str(random.randint(111111, 99999999))
                                    )
                                    break
                                if event_nf.type == VkEventType.MESSAGE_NEW and event_nf.user_id==MyId and event_nf.to_me and event_nf.text not in list(MenuMessages.values()):
                                    print("GOTCHA")
                                    message_items = vk.messages.getById(message_ids=event_nf.message_id)["items"]
                                    if message_items[0]["fwd_messages"] != []:
                                        MessageRules.update({message_items[0]["fwd_messages"][0]['peer_id']:[]})
                                        nf_chat_selected = message_items[0]["fwd_messages"][0]['peer_id']
                                        break
                                    else:
                                        vk.messages.send(  # Отправляем сообщение
                                            user_id=event_nf.user_id,
                                            message=MenuMessages['setting_mode_error_no_forward'],
                                            random_id=str(random.randint(111111, 99999999))
                                        )
                            if nf_chat_selected:
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.user_id,
                                    message=MenuMessages['new_filter_send_people_link'],
                                    random_id=str(random.randint(111111, 99999999))
                                )
                                for event_nf in longpoll.listen():
                                    if event_nf.type == VkEventType.MESSAGE_NEW and str(event_nf.text)[:4].lower() == "exit":
                                        vk.messages.send(  # Отправляем сообщение
                                            user_id=event_nf.user_id,
                                            message=MenuMessages['setting_mode_enable'],
                                            random_id=str(random.randint(111111, 99999999))
                                        )
                                        break
                                    if event_nf.type == VkEventType.MESSAGE_NEW and event_nf.user_id == MyId and event_nf.to_me and event_nf.text not in list(
                                            MenuMessages.values()):
                                        print("GOTCHA")
                                        MessageRules.update({nf_chat_selected : event_nf.text[17:]})
                                        vk.messages.send(  # Отправляем сообщение
                                            user_id=event_nf.user_id,
                                            message=MenuMessages['ned_filter_added'],
                                            random_id=str(random.randint(111111, 99999999))
                                        )
                                        print(MessageRules)
                                        break
                            nf_chat_selected = 0



                        else:
                            vk.messages.send(  # Отправляем сообщение
                                user_id=event.user_id,
                                message=MenuMessages['misunderstanding'],
                                random_id=str(random.randint(111111, 99999999))
                            )
            else:
                message_items = vk.messages.getById(message_ids=event.message_id)["items"]
                forwarded_from = []
                print(message_items[0]['peer_id'])
                if message_items[0]['peer_id'] in list(MessageRules.keys()):

                    for m in message_items[0]["fwd_messages"]:
                        forwarded_from.append(str(m["from_id"]))
                    print(forwarded_from)
                    print(MessageRules[message_items[0]['peer_id']])
                    if MessageRules[message_items[0]['peer_id']] in forwarded_from :
                         vk.messages.delete(message_ids = event.message_id)
                         print("deleted")


if __name__ == '__main__':
    main()
