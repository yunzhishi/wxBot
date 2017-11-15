#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json
import random


class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = "2715c50b39c54fa993fba5b1f2f938d3"
        self.robot_switch = True

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')

            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg_data, uid):
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[小蛋] ' + u'机器人已关闭！', uid)
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[小蛋] ' + u'机器人已开启！', uid)

    def emoticon_reply(self, uid):
        filename = './emoticons.json'
        with open(filename, 'r') as f:
            resource = json.load(f)
        # Random select from nx2 list 'resource', and take value of key 'md5'
        md5 = random.choice(resource)['md5']
        self.send_emoticon_by_uid(md5, uid)
        print '    ROBOT: [Emoticon MD5]', md5

    def handle_msg_all(self, msg):
        emoticon_cmd = [u'尬图', u'来啊', u'互相伤害啊']

        # if not self.robot_switch and msg['msg_type_id'] != 1:
        #     return

        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg['content']['data'], msg['user']['id'])

        elif msg['msg_type_id'] == 4:  # message from contact
            if msg['content']['type'] == 0: # text message
                if not self.robot_switch:
                    self.auto_switch(msg['content']['data'], msg['user']['id'])
                    return
                else:
                    self.auto_switch(msg['content']['data'], msg['user']['id'])

                textcmdFlag = False
                for cmd in emoticon_cmd:
                    if cmd == msg['content']['data']:
                        self.emoticon_reply(msg['user']['id'])
                        textcmdFlag = True
                if textcmdFlag == False:
                    self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
            else:
                # reply = u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                # self.send_msg_by_uid(reply, msg['user']['id'])
                # print '    ROBOT:', reply
                if not self.robot_switch:
                    return
                self.emoticon_reply(msg['user']['id'])

        elif msg['msg_type_id'] == 3:  # group message
            if msg['content']['type'] == 0:  # text message
                if not self.robot_switch:
                    self.auto_switch(msg['content']['data'], msg['user']['id'])
                    return
                else:
                    self.auto_switch(msg['content']['data'], msg['user']['id'])

                textcmdFlag = False
                for cmd in emoticon_cmd:
                    if cmd == msg['content']['data']:
                        self.emoticon_reply(msg['user']['id'])
                        textcmdFlag = True
                if textcmdFlag == False:
                    if 'detail' in msg['content']:
                        my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                        if my_names is None:
                            my_names = {}
                        if 'NickName' in self.my_account and self.my_account['NickName']:
                            my_names['nickname2'] = self.my_account['NickName']
                        if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                            my_names['remark_name2'] = self.my_account['RemarkName']

                        is_at_me = False
                        for detail in msg['content']['detail']:
                            if detail['type'] == 'at':
                                for k in my_names:
                                    if my_names[k] and my_names[k] == detail['value']:
                                        is_at_me = True
                                        break

                        if True:
                            if not self.robot_switch:
                                self.auto_switch(msg['content']['desc'], msg['user']['id'])
                                return
                            else:
                                self.auto_switch(msg['content']['desc'], msg['user']['id'])

                            textcmdFlag = False
                            for cmd in emoticon_cmd:
                                if cmd == msg['content']['desc']:
                                    self.emoticon_reply(msg['user']['id'])
                                    textcmdFlag = True
                            if textcmdFlag == False:
                                # src_name = msg['content']['user']['name']
                                # reply = '@' + src_name + ': '
                                # reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                                reply = self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                                self.send_msg_by_uid(reply, msg['user']['id'])
            else:
                # reply = u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                # self.send_msg_by_uid(reply, msg['user']['id'])
                # print '    ROBOT:', reply
                if not self.robot_switch:
                    return
                self.emoticon_reply(msg['user']['id'])


def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'

    bot.run()


if __name__ == '__main__':
    main()

