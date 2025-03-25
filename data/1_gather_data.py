from dotenv import load_dotenv
from os import getenv
import requests
import pandas as pd

load_dotenv(".env")

API_KEY = getenv("API_KEY")

handle = "kraigadams"

API = "https://www.googleapis.com/youtube/v3"

# get 'uploads' playlist ID
resp = requests.get(API+"/channels", params={"key":API_KEY, "forHandle":handle, "part": "contentDetails"})
if resp.status_code != 200:
    print(f'Something went wrong! Response code {resp.status_code}, check content: {resp.json()}')
    exit()

playlist_id = resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"] 

params = {
    "key": API_KEY,
    "playlistId": playlist_id,
    "part": "snippet",
    "maxResults": 50  # 每次获取最大数量的视频
}

keyItems = ["publishedAt", "title", "description", "videoId"]
rows = []

print("开始获取视频数据...")
while True:  # 持续获取直到没有更多视频
    resp = requests.get(API+"/playlistItems", params=params)
    if resp.status_code != 200:
        print(f'Check response: {resp.status_code}, {resp.json()}')
        exit()

    resp = resp.json()
    
    for item in resp["items"]:
        item["snippet"]["videoId"] = item["snippet"]["resourceId"]["videoId"]
        rows.append({x: item["snippet"][x] for x in keyItems})
    
    print(f"已获取 {len(rows)} 个视频")
    
    # 检查是否还有更多视频
    if "nextPageToken" not in resp:
        print("所有视频都已获取完成！")
        break
        
    params["pageToken"] = resp["nextPageToken"]

export = pd.DataFrame(rows, columns=keyItems)
export.to_csv("data.csv")
print(f"总共获取了 {len(rows)} 个视频，数据已保存到 data.csv")