from django.db import models
from boto3.session import Session
import os
import sys
import json

"""reload intepretor, add credential path"""
reload(sys)
sys.setdefaultencoding('UTF8')

"""import credentials from root/AppCreds"""
with open(os.path.dirname(sys.path[0])+'/AppCreds/AWSAcct.json','r') as AWSAcct:
    awsconf = json.loads(AWSAcct.read())

dynamodb_session = Session(aws_access_key_id=awsconf["aws_access_key_id"],
              aws_secret_access_key=awsconf["aws_secret_access_key"],
              region_name="us-east-1")

dynamodb = dynamodb_session.resource('dynamodb')

table = dynamodb.Table("User")

# Create your models here.
class User():
	def __init__(self, id, passwd):
		self.id = id
		self.passwd = passwd
		self.verified = False


	def get_response_by_id(id):
    response = table.get_item(
        Key={
            'email': id
        }
    )
    return respoonse

	def verify_email(self):
		response = self.get_response_by_id(self.id)
		if 'Item' in response:
			return True
		else:
			return False

	def verify_passwd(self, response):
		response = self.get_response_by_id(self.id)
		item = response['Item']
		pwd = item['password']
		if pwd == self.passwd:
			self.verified = True
			return True
		else:
			return False



