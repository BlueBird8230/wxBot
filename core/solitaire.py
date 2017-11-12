# coding: utf-8
from core.wxbot import *
from configparser import ConfigParser
import json


class SolitaireBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = "bf5d6ec788c74bf984823c8467404739"
        self.switch = True

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print('tuling_key:', self.tuling_key)

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
                    result = result + u"【" + k['source'] + u"】 " + \
                             k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')

            print('    ROBOT:', result)
            return result
        else:
            return u"关我屁事"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.switch= False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.switch= True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def is_at_me(self, msg, my_names):
        is_at_me = False
        for detail in msg['content']['detail']:
            values = detail['value'].split(' ')
            for v in values:
                if v[0] == '@':
                    pass
            if detail['type'] == 'at':
                for k in my_names:
                    if my_names[k] and my_names[k] == detail['value']:
                        return True

    def handle_msg_all(self, msg):
        # reply to self
        if not self.switch:
            if ['msg_type_id'] == 1 and msg['content']['type'] == 0:
                self.auto_switch(msg)
            else:
                return

        # reply contacts
        elif msg['msg_type_id'] == 4:
            # check if command here
            if msg['content']['type'] == 0:
                self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])

        # reply group messages
        elif msg['msg_type_id'] == 3:
            if msg['content']['type'] == 0:  # group text message
                if 'detail' in msg['content']: # @ info included
                    # doesn't understand here
                    my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                    if my_names is None:
                        my_names = {}
                    if 'NickName' in self.my_account and self.my_account['NickName']:
                        my_names['nickname2'] = self.my_account['NickName']
                    if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                        my_names['remark_name2'] = self.my_account['RemarkName']

                    if self.is_at_me(msg, my_names):
                        src_name = msg['content']['user']['name']
                        reply = 'to ' + src_name + ': '
                        if msg['content']['type'] == 0:  # text message
                            reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                        else:
                            reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                        self.send_msg_by_uid(reply, msg['user']['id'])

'''
    def schedule(self):
        self.send_msg(u'张三', u'测试')
        time.sleep(1)
'''


def main():
    bot = SolitaireBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    bot.run()


if __name__ == '__main__':
    main()
