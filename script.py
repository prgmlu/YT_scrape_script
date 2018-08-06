from isodate import parse_duration
import pandas as pd
import numpy as np
import requests
import json

api_key="AIzaSyBH2ZPP3p6NEY1xPl9iBHoUbPGvUx06zkk"
CHANNEL_ID='UC2CIEOijLIjue--UXFBZ1dw'
parameters = {'part':'contentDetails',"key": api_key,'id':CHANNEL_ID}


url='https://www.googleapis.com/youtube/v3/channels'
response=requests.request(method='get',url=url,params=parameters)

play_list_id=json.loads(response.text)['items'][0]['contentDetails']['relatedPlaylists']['uploads']

url='https://www.googleapis.com/youtube/v3/playlists'
parameters={'key':api_key,
            'part': 'contentDetails', 'id':play_list_id}

response=requests.request(method='get',url=url,params=parameters)
item_count=json.loads(response.text)['items'][0]['contentDetails']['itemCount']

parameters = {"part": "contentDetails",
              "key": api_key,
               "playlistId":play_list_id,
              "maxResults":"50"
              }
              
url = "https://www.googleapis.com/youtube/v3/playlistItems"
response = requests.request(method="get", url=url, params=parameters)
dict_response = json.loads(response.text)

token=dict_response['nextPageToken']

vid_ids=[]
vid_ids+=[ item['contentDetails']['videoId'] for item in dict_response['items']]


def collect_vids(token):
    global vid_ids
    parameters = {"part": "contentDetails",
                  "key": api_key,
                   "playlistId":play_list_id,
                  "pageToken":token,
                  "maxResults":"50"
                  }
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    response = requests.request(method="get", url=url, params=parameters)
    dict_response = json.loads(response.text)
    page_token=dict_response.get('nextPageToken')
    vid_ids+=[(dict_response['items'][i]['contentDetails']['videoId']) for i in range(len(dict_response['items']))]
    return page_token


while(token):
    token=collect_vids(token)


items=[]
for i in range(0,item_count,50):
    # step of 50 because of the API Limit
    id_string=",".join(vid_ids[i:i+50])
    parameters = {"part":"statistics,snippet,contentDetails",
                    "key": api_key,
                   "id":id_string
                  }
    url = "https://www.googleapis.com/youtube/v3/videos"
    response = requests.request(method="get", url=url, params=parameters)
    d = json.loads(response.text)
    items+=d['items']


stats=[]


for i in range(item_count):
    #ugly as hell i know, but basically collects the dates, title, id etc for each video as a tuple
    #and appends them to stats, which we will use to construct a dataframe from
    stats.append(
    [items[i]['snippet']['publishedAt'],items[i]['snippet']['title'],items[i]['id'],
     items[i]['statistics'].get('viewCount') , items[i]['statistics'].get('likeCount'), 
     items[i]['statistics'].get('dislikeCount'), items[i]['statistics'].get('commentCount')
    , items[i]['contentDetails'].get('duration')]
        )
                        

df=pd.DataFrame(stats,columns=['date','title','id','view','likes','dislikes','comments','duration'])
df['date']=pd.to_datetime(df['date'])
df['duration']=df['duration'].apply(lambda x: parse_duration(x).seconds)

df.to_csv("data.csv",index=False)

