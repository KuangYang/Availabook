from boto3.dynamodb.conditions import Key, Attr
from boto3.session import Session
import os
import sys
import json
import operator
import datetime
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
"""reload intepretor, add credential path"""
reload(sys)
sys.setdefaultencoding('UTF8')

"""import credentials from root/AppCreds"""
with open(os.path.dirname(sys.path[0])+ '/Asite' + '/availabook/AppCreds/AWSAcct.json','r') as AWSAcct:
    awsconf = json.loads(AWSAcct.read())

dynamodb_session = Session(aws_access_key_id=awsconf["aws_access_key_id"],
              aws_secret_access_key=awsconf["aws_secret_access_key"],
              region_name="us-east-1")
dynamodb = dynamodb_session.resource('dynamodb')

table = dynamodb.Table("Preference")

def recommend(email):
    response = table.get_item(
        Key={
            'email': email
        }
    )
    if 'Item' not in response:
        table.put_item(
            Item={
                'email': email,
                'rating': [0,0,0,0,0,0,0,0,0,0]
            }
        )
        return newUser(email)
    else:
        return returnUser(email)

# for new registered user
def newUser(email):
    tb_user = dynamodb.Table("User")
    tb_event = dynamodb.Table("Event")
    res_1 = tb_user.get_item(
        Key={
            'email': email
        }
    )
    location = res_1['Item']['zipcode']
    res_2 = tb_event.scan(
        FilterExpression=Attr('zipcode').eq(location),
    )
    res_2_diff = tb_event.scan(
        FilterExpression=Attr('zipcode').ne(location),
    )
    items = res_2['Items']
    items_diff = res_2_diff['Items']
    dic = {}
    for item in items:
        EId = item['EId']
        fave = item['fave']
        popular = len(fave)
        dic[EId] = popular
    sorted_dic = sorted(dic.items(), key=operator.itemgetter(1), reverse=True)
    dic_diff = {}
    for item in items_diff:
        EId = item['EId']
        fave = item['fave']
        popular = len(fave)
        dic_diff[EId] = popular
    sorted_dic_diff = sorted(dic_diff.items(), key=operator.itemgetter(1), reverse=True)
    eventList = []
    for i in range(0,10):
        if i < len(sorted_dic):
            id = sorted_dic[i][0]
            res_3 = tb_event.get_item(
                Key={
                    'EId': id
                }
            )
            date = res_3['Item']['date']
            time = res_3['Item']['time']
            if isExpired(date, time):
                pass
            else:
                event = res_3['Item']
                eventList.append(event)
        else:
            pass
    length = len(eventList)
    if len(eventList) < 10:
        for i in range(length, 10):
            if i-length < len(sorted_dic_diff):
                id = sorted_dic_diff[i-len(eventList)][0]
                res_4 = tb_event.get_item(
                    Key={
                        'EId': id
                    }
                )
                date = res_4['Item']['date']
                time = res_4['Item']['time']
                if isExpired(date, time):
                    pass
                else:
                    event = res_4['Item']
                    eventList.append(event)
            else:
                pass
    return eventList


def returnUser(email):
    response = table.get_item(
        Key={
            'email': email
        }
    )
    rating_list = response['Item']['rating']
    if (len(set(rating_list)) <= 1):
        return newUser(email)
    else:
        return get_returnUser_recommend(email)


def isExpired(date, time):
    cur = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = cur.split(' ')
    curdate = cur[0].split('-')
    eventdate = date.split('-')
    curtime = cur[1].split(':')
    eventtime = time.split(':')
    if int(curdate[0]) < int(eventdate[0]):
        return False
    elif int(curdate[0]) == int(eventdate[0]) and int(curdate[1]) < int(eventdate[1]):
        return False
    elif int(curdate[0]) == int(eventdate[0]) and int(curdate[1]) == int(eventdate[1]) and int(curdate[2]) < int(eventdate[2]):
        return False
    elif int(curdate[0]) == int(eventdate[0]) and int(curdate[1]) == int(eventdate[1]) and int(curdate[2]) == int(eventdate[2]) \
        and int(curtime[0]) < int(eventtime[0]):
        return False
    elif int(curdate[0]) == int(eventdate[0]) and int(curdate[1]) == int(eventdate[1]) and int(curdate[2]) == int(eventdate[2]) \
        and int(curtime[0]) == int(eventtime[0]) and int(curtime[1]) < int(eventtime[1]):
        return False
    else:
        return True


# for not login user
def common():
    tb_event = dynamodb.Table("Event")
    event = tb_event.scan()
    items = event['Items']
    dic = {}
    for item in items:
        EId = item['EId']
        fave = item['fave']
        popular = len(fave)
        dic[EId] = popular
        sorted_dic = sorted(dic.items(), key=operator.itemgetter(1), reverse=True)
    eventList = []
    for i in range(0, 10):
        if i < len(sorted_dic):
            id = sorted_dic[i][0]
            res_3 = tb_event.get_item(
                Key={
                    'EId': id
                }
            )
            date = res_3['Item']['date']
            time = res_3['Item']['time']
            if isExpired(date, time):
                pass
            else:
                event = res_3['Item']
                eventList.append(event)
        else:
            pass
    return eventList

# get score
def user_based_similarity():
    tb_preference = dynamodb.Table("Preference")
    raw = tb_preference.scan()
    data = raw['Items']
    cols_count, rows_count = 10, len(data)
    matrix = [[0 for x in range(cols_count)] for y in range(rows_count)]
    for i in range(0, len(data)):
        rating =  data[i]['rating']
        for j in range(0, 10):
            matrix[i][j] = int(rating[j])
    train = np.array(matrix)
    print(train)
    user_similarity = pairwise_distances(train, metric='cosine')
    print(user_similarity)
    mean_user_rating = train.mean(axis=1)
    print(mean_user_rating)
    ratings_diff = (train - mean_user_rating[:, np.newaxis])
    print(ratings_diff)
    pred_user = mean_user_rating[:, np.newaxis] + user_similarity.dot(ratings_diff) / np.array(
        [np.abs(user_similarity).sum(axis=1)]).T
    return pred_user

def get_returnUser_recommend(email):
    tb_preference = dynamodb.Table("Preference")
    raw = tb_preference.scan()
    data = raw['Items']
    matrix = user_based_similarity()
    length = len(data)
    list = []
    for i in range(0, length):
        if data[i]['email'] == email:
            list = matrix[i]
    max_index, max_value = max(enumerate(list), key=operator.itemgetter(1))
    cluster_id = max_index
    return recommend_item(cluster_id)

def recommend_item(Cid):
    tb_event = dynamodb.Table("Event")
    recommendation_list = []
    events = tb_event.scan()
    eventlist = events['Items']
    for event in eventlist:
        clusterlist = event['label']
        if clusterlist[6] >= sum(clusterlist) / len(clusterlist):
            res_5 = tb_event.get_item(
                Key={
                    'EId': event['EId']
                }
            )
            date = res_5['Item']['date']
            time = res_5['Item']['time']
            if isExpired(date, time) == False:
                recommendation_list.append(event)
    return recommendation_list

def normalize(vec):
    return vec/np.sum(vec)

def cosine_similarity(user_vec,event_vec):
    ### not use it
    dot_product = np.dot(event_vec,user_vec)
    square_root_event = np.sqrt(np.sum(event_vec**2))
    square_root_user = np.sqrt(np.sum(user_vec**2))
    cosine_similarity = event_vec.dot(user_vec)/(square_root_user*square_root_event)
    return cosine_similarity

def time_score(event_date):
    today = datetime.date.today()
    e_year, e_month, e_day = event_date.split("-")
    event_date = datetime.date(int(e_year),int(e_month),int(e_day))
    date_diff = int((str(event_date - today)).split(" ")[0])
    return math.exp(-date_diff)

def distance_score(event_zipcode,user_zipcode):
    try:
        ### if zipcode is valid
        zipcode1 = zipcode.isequal(user_zipcode)
        zipcode2 = zipcode.isequal(event_zipcode)
        distance = math.sqrt((zipcode1.lon - zipcode2.lon)**2 + (zipcode1.lat-zipcode2.lat)**2)
        return math.exp(-distance)
    except:
        return None


def popularity_score(likes_num):
    return math.exp(-likes_num)/(1+math.exp(-likes_num))

def event_vec(event):
    ### think about put it into db to accelate the speed
    time_score = time_score(event.date)
    distance_score = distance_score(event.user.zipcode)
    topic_score = origin_recommend()
    event_vec = np.array([time_score,distance_score,topic_score])
    return normalize(event_vec)

def assign_score(user,event):
    event_vec = event_vec(event)
    return event_vec.dot(user.user_vec)

def para_tuning(user_vec,event_vec):
    ### user_vec and event_vec are normalized
    ### use this function whenever a new like,not post!
    return normalize(user_vec + 0.05*event_vec)


# user_table = dynamodb.Table("User")
# response = user_table.get_item(
#         Key={
#             'email': 'xuexun1994@gmail.com'
#         }
# )
# print(response['Item'])
# x = str(np.random.rand())
# user_table.update_item(
#     Key={
#     'email': 'xuexun1994@gmail.com'
# },
# UpdateExpression='SET rating = :val1',
# ExpressionAttributeValues={
#     ':val1': [x,0,x,0,x,x,x,x,x,x],
# }
# )
# print(get_returnUser_recommend('xuexun1994@gmail.com'))
