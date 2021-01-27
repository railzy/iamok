#_*_coding: utf-8 _*_
import time
import requests
import json
import re
import os
import execjs
import traceback
# import http.cookiejar as cj

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def submit():
    #账户信息
    user = os.environ["SCUT_USERNAME"]
    passwd = os.environ["SCUT_PASSWORD"]

    session = requests.Session()

    #登陆页面
    url_1 = 'https://sso.scut.edu.cn/cas/login?service=https%3A%2F%2Fiamok.scut.edu.cn%2Fcas%2Flogin'

    #利用des.js文件加密，得到登陆表单数据rsa
    r = session.get(url_1)
    lt = re.findall('name="lt" value="(.*?)"', r.text)[0]
    execution = re.findall('name="execution" value="(.*?)"', r.text)[0]

    with open('des.js') as f:
        ctx = execjs.compile(f.read())
    string1 = user + passwd + lt
    rsa = ctx.call('strEnc', string1, '1', '2', '3')

    #登陆所需的表单数据
    login_data = {
        'rsa': rsa,
        'ul': len(user),
        'pl': len(passwd),
        'lt': lt,
        'execution': execution,
        '_eventId': 'submit'
    }
    ##进行登陆登陆
    session.post(url_1, data=login_data)

    #optional，保存cookie到本地
    # session.cookies.save('cookie.txt', ignore_discard=True, ignore_expires=True)

    #get请求链接，解析你的健康数据
    url_2 = 'https://iamok.scut.edu.cn/mobile/recordPerDay/getRecordPerDay'
    html = session.get(url_2)
    submit_data = html.json()['data']

    #post请求链接，提交新的健康数据
    url_3 = 'https://iamok.scut.edu.cn/mobile/recordPerDay/submitRecordPerDay'
    output = session.post(url_3, json=submit_data)
    print(output.text)
    return output

def push_notices(text, desp=''):
    serverchan_url = 'https://sc.ftqq.com/'
    serverchan_key = os.environ["SERVERCHAN_KEY"]
    post_url = serverchan_url + serverchan_key + '.send'
    postdata = {'text': text, 'desp': desp}
    requests.get(post_url, postdata)

code = 500
if __name__ == "__main__":
    try:
        while code != 200:
            output = submit()
            code = json.loads(output.text)["code"]
    except BaseException as e:
        msg = traceback.format_exc()
        print(msg)
        print("健康信息提交失败！")
        push_notices('健康信息提交失败！', msg)
    else:
        print("您已成功提交健康信息！")
        push_notices("您已成功提交健康信息！")
    


