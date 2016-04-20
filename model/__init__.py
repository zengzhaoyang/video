#-*-coding:utf-8-*-

class MongoDB:
	def __init__(self):
		from pymongo import MongoClient
		self.con = MongoClient('localhost')
		self.db = self.con.challenge

class RedisDB:
	def __init__(self):
		from redis import Redis
		self.con = Redis('localhost')
