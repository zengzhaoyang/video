#-*-coding:utf-8-*-

from config import *

import smtplib
from email.mime.text import MIMEText
from email.header import Header

def generate_session():
    import os
    from model import RedisDB
    con = RedisDB().con
    code = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(16)))
    while True:
        if con.sismember('session',code) == False:
            con.sadd('session',code)
            break
        code = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(16)))
    return code

def send_email(member, message):
    # import requests
    # url = 'http://182.92.104.30/mail'
    # data = {
    #     'fromuser':'MSChallenge <root@ms-multimedia-challenge.com>',
    #     'touser':'tmei@microsoft.com',
    #     'subject':'[MS Challenge Notice]',
    #     'message':'No reply\nMS Multimedia Register\n'
    # }
    # mem = []
    # for item in member:
    #     one = '%s %s %s\n'%(item['name'], item['email'], item['organization'])
    #     mem.append(one)
    # data['message'] = data['message'] + ''.join(mem)
    # res = requests.post(url, data=data)
    # data['touser'] = 'tiyao@microsoft.com'
    # res = requests.post(url, data=data)

    smtp = smtplib.SMTP('localhost')
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = Header("MS-MULTIMEDIA-CHALLENGE<root@ms-multimedia-challenge.com>")
    msg['To'] = Header(member)
    msg['Subject'] = '[MS-MULTIMEDIA-CHALLENGE Notice]'
    print member
    try:
        smtp.sendmail("root@ms-multimedia-challenge.com", [member], msg.as_string())
        return 'ok'
    except:
        return 'error'


def check_team_member(challenge_type, username, password, team_name, member):

    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    one = register_team.find_one({'username':username})
    if one != None:
        return False, USER_NAME_UNAVALIABLE, 0
    one = register_team.find_one({'teamname':team_name})
    if one != None:
        return False, TEAM_NAME_UNAVALIABLE, 0

    length = len(member)
    for i in range(length):
        for j in range(i+1, length):
            if member[i]['name'] == member[j]['name'] and member[i]['email'] == member[j]['email']:
                return false, MEMBER_UNAVALIABLE, j

    register_member = db.register_member
    # for i in range(length):
    #     one = register_member.find_one({'name':member[i]['name'], 'email':member[i]['email']})
    #     if one != None:
    #         return False, MEMBER_UNAVALIABLE, i
    import hashlib
    _id = register_team.insert({
        'username':username,
        'password':hashlib.md5(password).hexdigest(),
        'teamname':team_name,
        'member':member})
    team_id = str(_id)
    # for i in range(length):
    #     if i == 0:
    #         register_member.insert({
    #             'name':member[i]['name'],
    #             'email':member[i]['email'],
    #             'organization':member[i]['organization'],
    #             'team_id':team_id,
    #             'is_caption':True})
    #     else:
    #         register_member.insert({
    #             'name':member[i]['name'],
    #             'email':member[i]['email'],
    #             'organization':member[i]['organization'],
    #             'team_id':team_id,
    #             'is_caption':False})

    from model import RedisDB
    con = RedisDB().con
    code = generate_session()
    key = 'session2teamid:' + code
    value = team_id + '&' +challenge_type
    con.set(key, value)
    con.expire(key, 7200)

    return True, SUCCESS, code

def update_team_member(challenge_type, team_id, teamname, member):
    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    from bson import ObjectId
    _id = ObjectId(team_id)
    
    length = len(member)
    for i in range(length):
        for j in range(i+1, length):
            if member[i]['name'] == member[j]['name'] and member[i]['email'] == member[j]['email']:
                return false, MEMBER_UNAVALIABLE, j
    # for i in range(length):
    #     one = register_member.find_one({'name':member[i]['name'], 'email':member[i]['email']})
    #     if one != None and one['team_id'] != team_id:
    #         return False, MEMBER_UNAVALIABLE, i

    one = register_team.find_one({'_id':_id})
    if one == None:
        return False, TEAM_NOT_EXIST, 0

    register_team.update({'_id':_id}, {'$set':{'teamname':teamname, 'member':member}})
    return True, SUCCESS, 0


def auth(challenge_type, username, password):

    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    import hashlib
    one = register_team.find_one({
        'username':username,
        'password':hashlib.md5(password).hexdigest()
        })
    if one == None:
        return False, ''
    else:
        from model import RedisDB
        con = RedisDB().con
        code = generate_session()
        key = 'session2teamid:' + code
        value = str(one['_id']) + '&' +challenge_type
        con.set(key, value)
        con.expire(key, 7200)
        return True, code

def get_teamid_by_session(session):
    from model import RedisDB
    con = RedisDB().con
    key = 'session2teamid:'+session
    value = con.get(key)
    if value != None:
        con.expire(key, 7200)
    return value

def get_info_by_session(session):
    temp = get_teamid_by_session(session)
    if temp == None:
        return False, ''

    team_id, challenge_type = temp.split('&')

    from bson import ObjectId
    _id = ObjectId(team_id)
    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    one = register_team.find_one({'_id':_id})
    if 'hasSubmit' in one:
        flag = True
    else:
        flag = False
    if 'hasSubmitReport' in one:
        flag2 = True
    else:
        flag2 = False
    res = {
        'teamname':one['teamname'],
        'member':one['member'],
        'hasSubmit':flag,
        'hasSubmitReport':flag2
    }
    return True, res

def team_submit(temp):
    team_id, challenge_type = temp.split('_')
    from bson import ObjectId
    _id = ObjectId(team_id)
    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    register_team.update({'_id':_id}, {'$set':{'hasSubmit':True}})

def team_submit_report(temp):
    team_id, challenge_type = temp.split('_')
    from bson import ObjectId
    _id = ObjectId(team_id)
    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    register_team.update({'_id':_id}, {'$set':{'hasSubmitReport':True}})

def get_all_team(challenge_type):
    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    all_team = register_team.find()
    res = []
    for item in all_team:
        temp = {
            'teamname':item['teamname'],
            'member':item['member'],
        }
        if 'hasSubmit' in item:
            temp['hasSubmit'] = True
        else:
            temp['hasSubmit'] = False
        if 'hasSubmitReport' in item:
            temp['hasSubmitReport'] = True
        else:
            temp['hasSubmitReport'] = False
        res.append(temp)
    return res

def check_and_send_reset_password_email(challenge_type, team_name, caption_name, caption_email):
    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    one = register_team.find_one({'teamname':team_name})
    if one == None:
        return False
    member = one['member']
    if member[0]['name'] == caption_name and member[0]['email'] == caption_email:
        code = generate_session()
        from model import RedisDB
        con = RedisDB().con
        con.set('session2password:' + code, str(one['_id']))
        con.expire('session2password:' + code, 21600)

        print caption_email

        send_email(caption_email, 'No reply\nClick the following link to reset the password in 30 minutes.\nhttp://ms-multimedia-challenge.com/reset?token=%s&challenge_type=video'%code)
        # import requests
        # url = 'http://182.92.104.30/mail'
        # data = {
        #     'fromuser':'MSChallenge <root@ms-multimedia-challenge.com>',
        #     'touser':caption_email,
        #     'subject':'[MS Challenge Notice]',
        #     'message':
        # }
        # res = requests.post(url, data=data)
        # data['touser'] = '13631252971@163.com'
        # res = requests.post(url, data=data)
        return True
    else:
        return False

def get_reset_info_by_token(token, challenge_type):
    from model import RedisDB
    con = RedisDB().con
    teamid = con.get('session2password:' + token)
    if teamid == None:
        return False, ''
    from bson import ObjectId
    _id = ObjectId(teamid)
    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    one = register_team.find_one({'_id':_id})
    if one == None:
        return False, ''
    else:
        info = {}
        info['username'] = one['username']
        info['teamname'] = one['teamname']
        info['captionname'] = one['member'][0]['name']
        return True, info

def reset_password_by_token(challenge_type, token, username, teamname, captionname, password):
    from model import RedisDB
    con = RedisDB().con
    teamid = con.get('session2password:' + token)
    if teamid == None:
        return False, ''
    from bson import ObjectId
    _id = ObjectId(teamid)

    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    one = register_team.find_one({'_id':_id})
    if one == None:
        return False, ''
    else:
        if one['username'] != username or one['teamname'] != teamname or one['member'][0]['name'] != captionname:
            return False, ''
        import hashlib
        register_team.update({'_id':_id}, {'$set':{'password':hashlib.md5(password).hexdigest()}})
        code = generate_session()
        key = 'session2teamid:' + code
        value = teamid + '&' +challenge_type
        con.set(key, value)
        con.expire(key, 7200)
        return True, teamid

