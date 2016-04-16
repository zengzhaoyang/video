#-*-coding:utf-8-*-

from config import *

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

def send_email(member):
    pass

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
    for i in range(length):
        one = register_member.find_one({'name':member[i]['name'], 'email':member[i]['email']})
        if one != None:
            return False, MEMBER_UNAVALIABLE, i

    _id = register_team.insert({
        'username':username,
        'password':password,
        'teamname':team_name,
        'member':member})
    team_id = str(_id)
    for i in range(length):
        if i == 0:
            register_member.insert({
                'name':member[i]['name'],
                'email':member[i]['email'],
                'organization':member[i]['organization'],
                'team_id':team_id,
                'is_caption':True})
        else:
            register_member.insert({
                'name':member[i]['name'],
                'email':member[i]['email'],
                'organization':member[i]['organization'],
                'team_id':team_id,
                'is_caption':False})

    from model import RedisDB
    con = RedisDB().con
    code = generate_session()
    key = 'session2teamid:' + code
    value = team_id + '&' +challenge_type
    con.set(key, value)
    con.expire(key, 7200)

    return True, SUCCESS, code

def auth(challenge_type, username, password):

    from model import MongoDB
    db = MongoDB().db
    register_team = eval("db.%s"%challenge_type)
    one = register_team.find_one({
        'username':username,
        'password':password
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
    res = {
        'teamname':one['teamname'],
        'member':one['member']
    }
    return True, res