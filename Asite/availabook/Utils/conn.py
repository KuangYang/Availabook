# This is a simple connection to DynamoDB with get/put/update/delete function
# Please fill in the Aceess_key and Secret_access_key first
# Please create a table named "User" with the following columns:
# id | first_name | last_name

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

# get function
def get():
    response = table.get_item(
        Key={
            'email': "xx@gmail.com"
        }
    )
    item = response['Item']
    print(item)

# put function
def put(email, first_name, last_name):
    table.put_item(
        Item={
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        }
    )

# update function
def update(email, first_name, last_name):
    table.update_item(
        Key={
            'email': email
        },
        UpdateExpression='SET first_name = :val1, last_name = :val2',
        ExpressionAttributeValues={
            ':val1': first_name,
            ':val2': last_name
        }
    )

# delete function
def delete(email):
    table.delete_item(
        Key={
            'email': email
        }
    )

if __name__ == '__main__':
    get()
