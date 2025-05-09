#!/usr/bin/env python
# coding: utf-8

# In[9]:


import os
import time
import sqlite3
import googleapiclient.discovery
import pandas as pd
from googleapiclient.errors import HttpError


# In[10]:


# Set up YouTube API
#API 1: *************************************
#API 2: ************************************
#API 3: ************************************
youtube = googleapiclient.discovery.build(
    "youtube", "v3", developerKey="**************************"
)


# In[11]:


# Connect to SQLite and create tables
conn = sqlite3.connect("youtube.db")
cursor = conn.cursor()


# In[12]:


df =pd.read_sql_query('''Select * from Channels ''', conn)
len(df)


# In[13]:


# cursor.execute(''' Update Channels set processed = 0''')
# conn.commit()


# In[14]:


# Function to get all makeup videos from a channel with pagination and retry logic
def get_makeup_videos(channel_id):
    videos = []
    next_page_token = None

    while True:
        try:
            request = youtube.search().list(
                part="id",
                channelId=channel_id,
                q="makeup tutorial",
                type="video",
                order="viewCount",
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
        except HttpError as e:
            if e.resp.status in [403, 429]:
                print("Rate limit exceeded. Sleeping for 10 minutes...")
                time.sleep(600)
                continue
            else:
                print(f"HTTP error occurred: {e}")
                break

        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        if not video_ids:
            break

        try:
            video_request = youtube.videos().list(
                part="snippet,statistics",
                id=','.join(video_ids)
            )
            video_response = video_request.execute()
        except HttpError as e:
            print(f"Error fetching video details: {e}")
            break

        for item in video_response["items"]:
            stats = item["statistics"]
            snippet = item["snippet"]
            videos.append({
                "video_id": item["id"],
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "tags": ", ".join(snippet.get("tags", [])),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "published_date": snippet["publishedAt"]
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


# In[15]:


# Optional filter by ethnicity
ethnicity_filter = None  # e.g., "East Asian"
filter_query = """SELECT * FROM Channels WHERE processed = 0 and Face_Shape in ('Oblong','Heart','Square','Oval','Round')"""
if ethnicity_filter:
    filter_query += f" AND ethnicity = '{ethnicity_filter}'"

channels_df = pd.read_sql_query(filter_query, conn)


# In[17]:


# Fetch and store videos
for _, row in channels_df.iterrows():
    print(f"Processing channel: {row['channel_name']} ({row['channel_id']})")
    videos = get_makeup_videos(row["channel_id"])
    for vid in videos:
        cursor.execute('''
            INSERT OR IGNORE INTO Videos_new (video_id, channel_id, channel_name, ethnicity, title, description, tags, url, views, likes, comments,Publish_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        ''', (
            vid["video_id"],
            row["channel_id"],
            row["channel_name"],
            row["ethnicity"],
            vid["title"],
            vid["description"],
            vid["tags"],
            vid["url"],
            vid["views"],
            vid["likes"],
            vid["comments"],
            vid["published_date"]
        ))
    cursor.execute('''
        UPDATE Channels SET processed = 1 WHERE channel_id = ? AND ethnicity = ?
    ''', (row["channel_id"], row["ethnicity"]))
    conn.commit()

print("Makeup video details saved to SQLite database.")
# conn.close()


# In[ ]:


filter_query = """SELECT * FROM Videos_new """
# if ethnicity_filter:
#     filter_query += f" AND ethnicity = '{ethnicity_filter}'"

videos_df = pd.read_sql_query(filter_query, conn)


# In[ ]:


len(videos_df)


# In[ ]:




