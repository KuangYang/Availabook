from django.db import models
from boto3.session import Session
import os
import sys
import json

"""reload intepretor, add credential path"""
reload(sys)
sys.setdefaultencoding('UTF8')

"""import credentials from root/AppCreds"""

print "path: " + os.path.dirname(sys.path[0])
with open(os.path.dirname(sys.path[0])+ '/Asite' + '/availabook/AppCreds/AWSAcct.json','r') as AWSAcct:
    awsconf = json.loads(AWSAcct.read())

dynamodb_session = Session(aws_access_key_id=awsconf["aws_access_key_id"],
              aws_secret_access_key=awsconf["aws_secret_access_key"],
              region_name="us-east-1")

dynamodb = dynamodb_session.resource('dynamodb')

user_table = dynamodb.Table("User")
event_table = dynamodb.Table("Event")
# Create your models here.
class User():
    #def __init__(self, id, passwd, passwd_again, firstname, lastname, age, city, zipcode):
    def __init__(self, id, passwd):
        self.id = id
        self.passwd = passwd
        #self.passwd_again = passwd_again
        #self.firstname = firstname
        #self.lastname = lastname
        #self.age = age
        #self.city = city
        #self.zipcode = zipcode
        self.verified = False


    def check_input_passwd(self):
        if passwd == passwd_again:
            return True
        else:
            return False

    def push_to_dynamodb(self):
        if verify_email() == False:
            if check_input_passwd() == True:
                user_table.put_item(
                    Item={
                        'email': self.id,
                        'age': self.age,
                        'city': self.city,
                        'first_name': self.firstname,
                        'last_name': self.lastname,
                        'password': self.password,
                        'zipcode': self.zipcode,
                    }
                )

    def get_response_by_id(self, id):
        response = user_table.get_item(
            Key={
                'email': id
            }
        )
        return response

    def authen_user(self):
	    return self.verify_email() and self.verify_passwd()

    def verify_email(self):
    	#user_id = self.id
        response = self.get_response_by_id(self.id)
        if 'Item' in response:
            return True
        else:
            return False

    def verify_passwd(self):
    	#user_id = self.id
        response = self.get_response_by_id(self.id)
        item = response['Item']
        pwd = item['password']
        if pwd == self.passwd:
            return True
        else:
            return False
        return False

    def authorize(self):
        self.verified = True


class Event():
    def __init__(self,EId,content,date,time,label,place):
        self.EId = EId  ### use hadhid, to be modify
        self.content = content
        self.date = date
        self.time = time
        self.label = label
        self.like = []
        self.place = place
    ### put function
    def put_into_db(self,EId,content,date,label,like,place,time):
        event_table.put_item(
        Item={
            'EId': EId,
            'content': content,
            'date': date,
            'time': time,
            'label': label,
            'like': like,
            'place': place,
        }
    )
    ### get function, get_response first then use responce to get items
    def get_response_by_EId(EId):
        response = event_table.get_item(
            Key = {
                'EId':EId
            }
        )
        return response

    def get_content(response):
        return response['content']
    def get_date(response):
        return response['date']
    def get_time(response):
        return response['time']
    def get_label(response):
        return response['label']
    def get_like(response):
        return response['like']
    def get_place(response):
        return response['place']
    ### delete function
    def delete(EId):
        event_table.delete_item(
            Key={
                'EId': EId
            }
        )
    ### auxiliary function
    def get_like_num(response):
        return len(response['like'])



