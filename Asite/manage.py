#!/usr/bin/env python
import os
import sys
import json

"""reload intepretor, add credential path"""
reload(sys)
sys.setdefaultencoding('UTF8')

"""import credentials from root/AppCreds"""
with open(os.path.dirname(sys.path[0])+'/AppCreds/AWSAcct.json','r') as AWSAcct:
    awsconf = json.loads(AWSAcct.read())
aws_access_key_id=awsconf["aws_access_key_id"],
aws_secret_access_key=awsconf["aws_secret_access_key"]

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Asite.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
