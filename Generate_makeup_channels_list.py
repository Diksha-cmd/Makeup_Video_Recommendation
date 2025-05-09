#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import googleapiclient.discovery
import pandas as pd

# Set up YouTube API
youtube = googleapiclient.discovery.build(
    "youtube", "v3", developerKey="**************"
)


# In[2]:


# Ethnicity-specific search queries
queries = {
    "South Asian/Indian": [
        "Top Indian makeup channels",
        "Popular Indian beauty vloggers",
        "Best South Asian makeup gurus",
        "Indian beauty YouTubers",
        "Famous desi makeup channels",
    ],
    "East Asian": [
        "Popular Korean makeup channels",
        "Top Asian beauty vloggers",
        "Best Chinese makeup YouTubers",
        "Japanese makeup guru channels",
        "Famous East Asian beauty bloggers",
    ],
    "Black/African-American": [
        "Popular Black makeup channels",
        "Top African-American beauty YouTubers",
        "Best Black beauty vloggers",
        "Famous Black makeup gurus",
        "Top makeup channels for dark skin",
    ],
    "Latinx/Hispanic": [
        "Best Latina makeup channels",
        "Popular Hispanic beauty vloggers",
        "Top Latinx beauty gurus",
        "Famous Mexican beauty YouTubers",
        "Trending Latina makeup bloggers",
    ],
    "White/Caucasian": [
        "Top Caucasian beauty channels",
        "Popular European makeup vloggers",
        "Best White beauty YouTubers",
        "Famous makeup guru channels Caucasian",
        "Trending makeup channels for fair skin",
    ],
}


# In[3]:


# Data storage
data = []
seen_channels = {ethnicity: set() for ethnicity in queries}

# Loop through queries and fetch channel data
for ethnicity, ethnicity_queries in queries.items():
    for query in ethnicity_queries:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="channel",
            regionCode="US",
            relevanceLanguage="en",
            maxResults=50
        )
        response = request.execute()

        for item in response["items"]:
            channel_id = item["id"]["channelId"]

            if channel_id in seen_channels[ethnicity]:
                continue

            seen_channels[ethnicity].add(channel_id)
            channel_title = item["snippet"]["title"]
            thumbnail = item["snippet"]["thumbnails"]["default"]["url"]
            url = f"https://www.youtube.com/channel/{channel_id}"

            # Fetch additional statistics like subscribers and views
            stats_request = youtube.channels().list(
                part="statistics",
                id=channel_id
            )
            stats_response = stats_request.execute()

            stats = stats_response["items"][0]["statistics"]
            subs = stats.get("subscriberCount", "N/A")
            views = stats.get("viewCount", "N/A")

            data.append({
                "Ethnicity": ethnicity,
                "Channel Name": channel_title,
                "Channel ID": channel_id,
                "Thumbnail": thumbnail,
                "URL": url,
                "Subscribers": subs,
                "Views": views
            })


# In[7]:


# Save data to CSV
channels_df = pd.DataFrame(data)
channels_df.to_csv("/Users/dikshatiwari/Documents/Youtube_search/youtube_makeup_channels.csv", index=False)
channels_df.head()


# In[5]:


len(channels_df)


# In[6]:


channels_df.groupby(['Ethnicity']).size().reset_index(name='counts')


# In[ ]:




