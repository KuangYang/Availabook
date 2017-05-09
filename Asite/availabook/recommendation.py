from boto3.dynamodb.conditions import Key, Attr
from boto3.session import Session
import os
import sys
import json
import operator
import datetime
import time
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from threading import Thread
import nltk
from nltk.corpus import wordnet as wn
import math
import json
from geopy.geocoders import Nominatim
"""reload intepretor, add credential path"""
reload(sys)
sys.setdefaultencoding('UTF8')
nltk.data.path.append(os.path.dirname(sys.path[0])+'/Asite/availabook/Utils/nltk_data')
"""import credentials from root/AppCreds"""
with open(os.path.dirname(sys.path[0])+'/Asite/availabook/AppCreds/AWSAcct.json','r') as AWSAcct:
    awsconf = json.loads(AWSAcct.read())

dynamodb_session = Session(aws_access_key_id=awsconf["aws_access_key_id"],
              aws_secret_access_key=awsconf["aws_secret_access_key"],
              region_name="us-east-1")
dynamodb = dynamodb_session.resource('dynamodb')
preference_table = dynamodb.Table("Preference")
tb_user = dynamodb.Table("User")
tb_event = dynamodb.Table("Event")
tb_fave = dynamodb.Table("Fave")
tb_result = dynamodb.Table("Result")


def postpone(function):
  def decorator(*args, **kwargs):
    t = Thread(target = function, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
  return decorator


def recommend(email):
    response = preference_table.get_item(
        Key={
            'email': email
        }
    )
    if 'Item' not in response:
        preference_table.put_item(
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
    response = preference_table.get_item(
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
            matrix[i][j] = float(rating[j])
    train = np.array(matrix)
    user_similarity = pairwise_distances(train, metric='cosine')
    mean_user_rating = train.mean(axis=1)
    ratings_diff = (train - mean_user_rating[:, np.newaxis])
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
        clusterlist = [float(i) for i in clusterlist]
        if clusterlist[Cid] >= sum(clusterlist) / len(clusterlist):
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

def time_score(event_date,event_time):
    today = datetime.date.today()
    e_year, e_month, e_day = event_date.split("-")
    print(event_time)
    e_hour,e_minute = event_time.split(":")
    print('event time '+str(e_hour)+str(e_minute))
    event_date = datetime.date(int(e_year),int(e_month),int(e_day))
    event_datetime = datetime.datetime(int(e_year),int(e_month),int(e_day),int(e_hour),int(e_minute))
    if event_date == today:
        if datetime.datetime.utcnow()>event_datetime:
            print(datetime.datetime.utcnow())
            print(event_datetime)
            return 0
        else:
            return 1
    date_diff = int((str(event_date - today)).split(" ")[0])
    #### set the threshold, if bigger than assign a penalty to discard this result
    try:
        result = math.exp(-0.16*date_diff) ### scale the result to make it same as distance
    except Exception as x:
        print(x)
        return 0
    if date_diff<0 or result < 0.1: ### old-of-date or later than 15 days
        result = 0
    return result

def distance_score(event_zipcode,user_zipcode):
    try:
        ### if zipcode is valid
        geolocator = Nominatim()
        location1 = geolocator.geocode(user_zipcode)  ### 10025(mahattan) to 07747(Aberdeen in new jersey) score is 0.681003758168
        location2 = geolocator.geocode(event_zipcode)
    except Exception as e:
        print('invalid zipcode')
        print(user_zipcode,event_zipcode)
        print(e)
        return 0
    distance = math.sqrt((location1.latitude - location2.latitude)**2 + (location1.longitude-location2.longitude)**2)
    result = math.exp(-0.58*distance)
    if result < 0.1:  ### distance farther than penn state to mahattan
        result = 0
    return result
    #### set the threshold, if bigger than assign a penalty to discard this result

def popularity_score(likes_num):
    likes_num = likes_num
    return (1-math.exp(-0.05*likes_num))

def vectorize(s_time,s_distance,s_popularity,s_topic):
    ### think about put it into db to accelate the speed
    vec = np.asarray([s_time,s_distance,s_popularity,s_topic])
    return normalize(vec)

def assign_score(user,event):
    event_vec = event_vec(event)
    return event_vec.dot(user.user_vec)

def para_tuning(user_vec,event_vec):
    ### user_vec and event_vec are normalized
    ### use this function whenever a new like,not post!
    return normalize(user_vec + 0.001*event_vec)

def get_label(data):
    try:
        w1 = [["outdoor", "ball", "sport", "swim", "happy"],
              ["study", "library", "computer", "read", "book"],
              ["cook", "restaurant", "food", "fish", "hungry"],
              ["moive", "theatre", "exibition", "photo", "masterpiece"],
              ["shopping", "shoes", "clothes", "discount", "mall"],
              ["market", "grocery", "fruit", "vegetable", "meat"],
              ["cat", "dog", "animal", "zoo", "bird"],
              ["sleep", "bed", "TV", "sofa", "chip"],
              ["drink", "bar", "beer", "cocktail", "wine"],
              ["hiking", "mountain", "sunshine", "drive", "park"]]
        w2 = [w.lower() for w in data.replace(',', ' ').split(' ')]
        similarity = []
        for i in range(0, 10):
            similarity.append((get_score(w1[i], w2)))
        similarity = normalize(np.asarray(similarity))
        return similarity
    except:
        print('get_label failed, return a default array')
        return np.ones(10)/10


def get_score(w1, w2):
    dict = {}
    for i in w2:
        for j in w1:
            scores = []
            s1 = wn.synsets(j)
            s2 = wn.synsets(i)
            for x in s1:
                for y in s2:
                    if x.wup_similarity(y) is not None:
                        scores.append(x.wup_similarity(y))
            if len(scores) != 0:
                dict[i + "," + j] = max(scores)
    dict_sorted = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
    return dict_sorted[0][1]



def update_para(email,event, like_or_post):
    ### use whenever like or post
    print(email)
    user = preference_table.get_item(
        Key={
            'email': email
        }
    )['Item']
    para = 0.2
    if like_or_post == 'post':
        para = 0.2
    elif like_or_post == 'like':
        para = 0.02
    else:
        print('not valid like_or_post')
    user_topic_vec = np.asarray([float(i) for i in user['rating']])
    print('before core_calculation')
    event_vec, event_topic_vec, user_hyper_vec, time_reward,distance_reward,event_valid,final_score = core_calculation(email,event,like_or_post)
    print('new event EId'+event['EId'])
    print('final_score '+str(final_score))
    rec_res = tb_result.get_item(
        Key={
            'email': email
        }
    )['Item']['rec_res']
    rec_res = json.loads(rec_res)
    rec_res[event['EId']]=final_score
    tb_result.update_item(
    Key={
        'email': email    
    },
    UpdateExpression='SET rec_res = :val1',
    ExpressionAttributeValues={
        ':val1': json.dumps(rec_res)
    }
    )
    print('new post into result_table')
    print('original hyper para: time, distance ,popularity, topic '+str(user_hyper_vec[0])+' ' +str(user_hyper_vec[1])+' '+str(user_hyper_vec[2])+' '+str(user_hyper_vec[3]))
    user_hyper_vec = normalize(user_hyper_vec + para*event_vec)    #### need to scale
    print('updated hyper para: time, distance ,popularity, topic '+str(user_hyper_vec[0])+' '+str(user_hyper_vec[1])+' '+str(user_hyper_vec[2])+' '+str(user_hyper_vec[3]))
    print('original user topic vec: '+str(user_topic_vec))
    user_topic_vec = normalize(user_topic_vec+ para*event_topic_vec)
    print('updated user topic vec: '+str(user_topic_vec))
    preference_table.update_item(
    Key={
        'email': email    
    },
    UpdateExpression='SET rating = :val1, time_para=:val2, distance_para=:val3,popularity_para=:val4,topic_para=:val5',
    ExpressionAttributeValues={
        ':val1': [str(i) for i in user_topic_vec.tolist()],
        ':val2': str(user_hyper_vec[0]),
        ':val3': str(user_hyper_vec[1]),
        ':val4': str(user_hyper_vec[2]),
        ':val5': str(user_hyper_vec[3]),
    }
    )
    print('finish update')

def recommend_to_all(event): #### run when post
    print('start recommend to all')
    user_list = tb_user.scan()['Items']
    for user in user_list:
        email = user['email']
        event_vec, event_topic_vec, user_hyper_vec, time_reward,distance_reward,event_valid,final_score = core_calculation(email,event,'post')
        rec_res = tb_result.get_item(
            Key={
                'email': email
            }
        )['Item']['rec_res']
        rec_res = json.loads(rec_res)
        rec_res[event['EId']]=final_score
        tb_result.update_item(
        Key={
            'email': email    
        },
        UpdateExpression='SET rec_res = :val1',
        ExpressionAttributeValues={
            ':val1': json.dumps(rec_res)
        }
        )
        print('recommend to '+email+' '+EId+' '+str(final_score))
    print('finish recommend to all')




def core_calculation(email,event,like_or_post):
    user = preference_table.get_item(
        Key={
            'email': email
        }
    )['Item']
    zipcode = tb_user.get_item(
        Key={
            'email':email
        }
    )['Item']['zipcode']
    EId = event['EId']
    event_valid = True  ### invalid if time, distance score is zero
    time_reward = False  ### reward if score is 1, menas today, add a value to the total score
    distance_reward = False  ## reward if score is 1, means add a value to the total score, since it is common sense that same place is important for event attending
    s_time =time_score(event['date'],event['time'])
    s_distance = distance_score(event_zipcode=str(event['zipcode']),user_zipcode=str(zipcode))
    s_popularity = popularity_score(len(event['fave']))
    if s_distance==0:
        print('invalid location')
        event_valid = False
    if s_time==0:
        print('invalid time')
        event_valid = False
    if s_time == 1:
        print('time reward')
        time_reward = True
    if s_distance == 1:
        print('distance reward')
        distance_reward = True
    event_topic_vec = get_label(event['content'])
    user_topic_vec = [float(i) for i in user['rating']]
    s_topic = cosine_similarity(np.asarray(user_topic_vec),np.asarray(event_topic_vec)) ## topicscore
    #print(user['time_para'],user['distance_para'],user['popularity_para'],user['topic_para'])
    event_vec = vectorize(s_time=s_time,s_distance=s_distance,s_popularity=s_popularity,s_topic=s_topic)
    user_hyper_vec = vectorize(s_time=float(user['time_para']),s_distance=float(user['distance_para']),s_popularity=float(user['popularity_para']),s_topic=float(user['topic_para']))
    if like_or_post == 'post':
        event_vec[2] = user_hyper_vec[2] #### if post, popularity keep the same
    final_score = np.dot(event_vec,user_hyper_vec)
    print('final_score of dot product '+str(final_score))
    if time_reward:
        final_score = final_score+ 0.03
    if distance_reward:
        final_score = final_score + 0.1
    if event_valid == False:
        final_score =0
    print('final_score after reward '+str(final_score))
    return event_vec, event_topic_vec, user_hyper_vec, time_reward,distance_reward,event_valid,final_score

def origin_recommend(email): ### run one time, can offline
    event_list = tb_event.scan()['Items']
    rec_res = {}
    i = 0
    for event in event_list:
        i +=1
        print(i)
        try:
            event_vec, event_topic_vec, user_hyper_vec, time_reward,distance_reward,event_valid,final_score = core_calculation(email,event)
            rec_res[event['EId']]=final_score
        except: ### invalid
            rec_res[event['EId']]=0
    tb_result.update_item(
    Key={
        'email': email    
    },
    UpdateExpression='SET rec_res = :val1',
    ExpressionAttributeValues={
        ':val1': json.dumps(rec_res)
    }
    )

def update_like_or_post_tag(email,event,like_or_post):
    if like_or_post == 'like':
        tb_result.update_item(
            Key={
                'email': email    
            },
            UpdateExpression='SET fave = :val1',
            ExpressionAttributeValues={
                ':val1': [email,event]
            }
        )
    elif like_or_post == 'post':
        tb_result.update_item(
            Key={
                'email': email    
            },
            UpdateExpression='SET post = :val1',
            ExpressionAttributeValues={
                ':val1': [email,event]
            }
        )


@postpone
def test_thread():
    while True:
        print('test thread')
        result_list = tb_result.scan()['Items']
        for result in result_list:
            like_or_not = result['fave']
            post_or_not = result['post']
            if post_or_not=='False' and like_or_not=='False':
                time.sleep(2)
            else:
                print(post_or_not)
                print(like_or_not)
                if post_or_not != 'False':
                    print('post is yes')
                    email = post_or_not[0]
                    event = post_or_not[1]
                    update_para(email,event,'post')
                    tb_result.update_item(
                        Key={
                            'email': email    
                        },
                        UpdateExpression='SET post = :val1',
                        ExpressionAttributeValues={
                            ':val1': 'False'
                        }
                    )
                if like_or_not != 'False':
                    print('like is yes')
                    email = like_or_not[0]
                    event = like_or_not[1]
                    update_para(email,event,'like')
                    tb_result.update_item(
                        Key={
                            'email': email    
                        },
                        UpdateExpression='SET fave = :val1',
                        ExpressionAttributeValues={
                            ':val1': 'False'
                        }
                    )

test_thread()
        #update_para('aa@qq.com','ac7e0f49-4217-4674-99be-2a1fa5e560fc','like')



#['580d7ee3-0e05-4e13-aae3-5ef677882930']

# result_list = tb_result.scan()['Items']
# print(result_list)

#origin_recommend('aa@qq.com')

#test_thread()

#user_event_scoring('aa@qq.com','ac7e0f49-4217-4674-99be-2a1fa5e560fc')

#print(time_score('2017-05-08'))
#print(distance_score('10027','15001'))
#print(popularity_score(1000))
# x = np.random.rand(10)
# x = normalize(x).tolist()
# preference_table.update_item(
# Key={
#     'email': 'aa@qq.com'    
# },
# UpdateExpression='SET rating = :val1, time_para=:val2, distance_para=:val3,popularity_para=:val4,topic_para=:val5',
# ExpressionAttributeValues={
#     ':val1': [str(i) for i in x],
#     ':val2': str(0.25),
#     ':val3': str(0.25),
#     ':val4': str(0.25),
#     ':val5': str(0.25),
# }
# )



# response = table.get_item(
#         Key={
#             'email': 'xx22@gmail.com'
#         }
# )
# x = np.random.rand(10)
# x = normalize(x).tolist()
# print([str(i) for i in x])
# preference_table.update_item(
#     Key={
#     'email': 'aa@qq.com'
# },
# UpdateExpression='SET rating = :val1',
# ExpressionAttributeValues={
#     ':val1': [str(i) for i in x],
# }
# )
# print(get_returnUser_recommend('xx22@gmail.com'))
