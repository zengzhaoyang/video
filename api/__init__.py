#-*-coding:utf-8-*-

from flask import Blueprint, request, jsonify, make_response
from config import *

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
	form = request.form
	required = ['challenge_type', 'username', 'password', 'teamname', 'caption_name', 'caption_email', 'caption_organization', 'member_num']
	for item in required:
		if not item in form:
			return jsonify(res=PARAMETER_ERROR)

	challenge_type = form['challenge_type']
	username = form['username']
	password = form['password']
	teamname = form['teamname']

	if username == "" or len(password) < 6 or teamname == "":
		return jsonify(res=PARAMETER_ERROR)

	caption_name = form['caption_name']
	caption_email = form['caption_email']
	caption_organization = form['caption_organization']

	if caption_name == "" or caption_email == "" or caption_organization == "":
		return jsonify(res=PARAMETER_ERROR)

	member_num = int(form['member_num'])
	member = [{
		'name':caption_name,
		'email':caption_email,
		'organization':caption_organization
	}]
	for i in range(1, member_num):
		required = ['member%d_name'%i, 'member%d_email'%i, 'member%d_organization'%i]
		for item in required:
			if not item in form:
				return jsonify(res=PARAMETER_ERROR)

		member_name = form['member%d_name'%i]
		member_email = form['member%d_email'%i]
		member_organization = form['member%d_organization'%i]

		if member_name == "" or member_email == "" or member_organization == "":
			return jsonify(res=PARAMETER_ERROR)

		member.append({
			'name':member_name,
			'email':member_email,
			'organization':member_organization
			})

	from lib import check_team_member
	status, err, place = check_team_member(challenge_type, username, password, teamname, member)
	if status == False:
		if err == TEAM_NAME_UNAVALIABLE:
			return jsonify(res=TEAM_NAME_UNAVALIABLE)
		elif err == USER_NAME_UNAVALIABLE:
			return jsonify(res=USER_NAME_UNAVALIABLE)
		else:
			return jsonify(res=MEMBER_UNAVALIABLE, place=place)
	else:
		from lib import send_email
		send_email(member)
		resp = jsonify(res=SUCCESS)
		resp.set_cookie('session', place)
		return resp

@api.route('/update', methods=['POST'])
def update():
	cookies = request.cookies
	if not 'session' in cookies:
		return jsonify(res=NOT_LOGIN)
	session = cookies['session']
	from lib import get_teamid_by_session
	teamid = get_teamid_by_session(session)
	if teamid == None:
		resp = jsonify(res=NOT_LOGIN)
		resp.delete_cookie('session')
		return resp
	teamid = teamid.split('&')[0]
	form = request.form
	required = ['challenge_type', 'teamname', 'caption_name', 'caption_email', 'caption_organization']
	for item in required:
		if not item in form:
			return jsonify(res=PARAMETER_ERROR)
	challenge_type = form['challenge_type']
	teamname = form['teamname']
	caption_name = form['caption_name']
	caption_email = form['caption_email']
	caption_organization = form['caption_organization']
	if caption_name == "" or caption_email == "" or caption_organization == "":
		return jsonify(res=PARAMETER_ERROR)

	member_num = int(form['member_num'])
	member = [{
		'name':caption_name,
		'email':caption_email,
		'organization':caption_organization
	}]
	for i in range(1, member_num):
		required = ['member%d_name'%i, 'member%d_email'%i, 'member%d_organization'%i]
		for item in required:
			if not item in form:
				return jsonify(res=PARAMETER_ERROR)

		member_name = form['member%d_name'%i]
		member_email = form['member%d_email'%i]
		member_organization = form['member%d_organization'%i]

		if member_name == "" or member_email == "" or member_organization == "":
			return jsonify(res=PARAMETER_ERROR)

		member.append({
			'name':member_name,
			'email':member_email,
			'organization':member_organization
			})

	from lib import update_team_member
	status, err, place = update_team_member(challenge_type, teamid, teamname, member)
	if status == True:
		return jsonify(res=SUCCESS)
	else:
		if err == TEAM_NAME_UNAVALIABLE:
			return jsonify(res=TEAM_NAME_UNAVALIABLE)
		elif err == USER_NAME_UNAVALIABLE:
			return jsonify(res=USER_NAME_UNAVALIABLE)
		elif err == TEAM_NOT_EXIST:
			return jsonify(res=TEAM_NOT_EXIST)
		else:
			return jsonify(res=MEMBER_UNAVALIABLE, place=place)

@api.route('/login', methods=['POST'])
def login():
	form = request.form
	required = ['challenge_type', 'username', 'password']
	for item in required:
		if not item in form:
			return jsonify(res=PARAMETER_ERROR)

	challenge_type = form['challenge_type']
	username = form['username']
	password = form['password']

	from lib import auth
	status, session = auth(challenge_type, username, password)
	if status == True:
		resp = jsonify(res=SUCCESS)
		resp.set_cookie('session', session)
		return resp
	else:
		return jsonify(res=USERNAME_OR_PASSWORD_ERROR)

@api.route('/logout', methods=['GET'])
def logout():
	resp = jsonify(res="00000")
	resp.delete_cookie('session')
	return resp

@api.route('/getinfo', methods=['GET'])
def getinfo():
	cookies = request.cookies
	if not 'session' in cookies:
		return jsonify(res=NOT_LOGIN)
	session = cookies['session']

	from lib import get_info_by_session
	status, info = get_info_by_session(session)
	if status == False:
		resp = jsonify(res=NOT_LOGIN)
		resp.delete_cookie('session')
		return resp
	else:
		return jsonify(res=SUCCESS, info=info)

@api.route('/submit', methods=['POST'])
def submit():
	cookies = request.cookies
	if not 'session' in cookies:
		return jsonify(res=NOT_LOGIN)
	session = cookies['session']

	from lib import get_teamid_by_session
	teamid = get_teamid_by_session(session)
	if teamid == None:
		resp = jsonify(res=NOT_LOGIN)
		resp.delete_cookie('session')
		return resp 

	teamid = teamid.replace('&', '_')

	files = request.files
	f = files['file']
	filename = f.filename
	filetype = filename.split('.')[-1]
	filename = teamid + '.' + filetype
	import os
	os.system("rm tmp/%s*"%teamid)
	f.save('tmp/' + filename)

	from lib import team_submit
	team_submit(teamid)

	return jsonify(res=SUCCESS)

@api.route('/allteam', methods=['GET'])
def allteam():
	args = request.args
	if not 'token' in args or not 'challenge_type' in args:
		return jsonify(res=PARAMETER_ERROR)
	token = args['token']
	if token != 'msramsmbest':
		return jsonify(res=PARAMETER_ERROR)
	challenge_type = args['challenge_type']
	from lib import get_all_team
	team = get_all_team(challenge_type)
	return jsonify(res=SUCCESS, team=team)
