from django.db import models
from boto3.session import Session
import os
import sys
import json
from availabook.recommendation import recommend, common
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
post_table = dynamodb.Table("Post")
# Create your models here.
class Users():
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


class Signup():
    def __init__(self, user_id, pwd, pwd_a, firstname, lastname, age, city, zipcode):
        self.id = user_id
        self.pwd = pwd
        self.pwd_a = pwd_a
        self.firstname = firstname
        self.lastname = lastname
        self.age = age
        self.city = city
        self.zipcode = zipcode
        self.picture = ''

    def add_picture(self, link):
        self.picture = link

    def push_to_dynamodb(self):
        user_table.put_item(
            Item={
                'email': self.id,
                'age': self.age,
                'city': self.city,
                'first_name': self.firstname,
                'last_name': self.lastname,
                'password': self.pwd,
                'zipcode': self.zipcode,
                'picture': str(self.picture),
            }
        )


class Event():
    def __init__(self,event): ### event means event['item'] in db
        self.EId = event['EId']  ### use hadhid, to be modify
        self.content = event['content']
        self.date = event['date']
        self.time = event['time']
        self.label = event['label']
        self.fave = event['fave']
        self.place = event['place']
        self.fave_num = str(len(event['fave']))
    ### delete function
    def delete(self,EId):
        event_table.delete_item(
            Key={
                'EId': self.EId
            }
        )
    ### auxiliary function
    def add_fave(self,user_email):
        self.fave.append(user_email)
        self.fave_num = str(len(self.fave))
        event_table.update_item(
            Key={
            'EId': self.EId
        },
        UpdateExpression='SET fave = :val1',
        ExpressionAttributeValues={
            ':val1': self.fave,
        }
        )


def put_event_into_db(EId,content,date,time,label,fave,place,timestamp,user_email):
    event_table.put_item(
        Item={
            'EId': EId,
            'content': content,
            'date': date,
            'time': time,
            'label': label,
            'fave': fave,
            'place': place,
        }
    )
    post_table.put_item(
        Item={
            'EId': EId,
            'email': user_email,
            'post_time': timestamp
        }
    )


def get_event_by_EId(EId):
    response = event_table.get_item(
        Key={
            'EId': EId
        }
    )
    return response['Item']


def get_event_list():
    ######## here need a iterator of dynamodb event table,then put them into event_list#######
    event_list = []
    response = event_table.scan(
    )
    tmp_list = response['Items']
    for e in tmp_list:
        event = Event(e)
        event_list.append(event)
    return event_list


def get_recommended_event_list(email):
    print "email recommendation:", email
    try:
        tmp_list = recommend(email)
    except:
        tmp_list = common()
    # print(tmp_list)
    event_list = []
    if tmp_list:
        for e in tmp_list:
            event = Event(e)
            event_list.append(event)
    return event_list








