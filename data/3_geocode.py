import pandas as pd
import requests
import time
import json
from dotenv import load_dotenv
import os

load_dotenv(".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def clean_location(location):
    if pd.isna(location) or location == "no location found":
        return None
    
    # 移除多余的空格和换行符
    location = location.strip()
    
    # 如果包含多个位置（用换行符分隔），只取第一个
    if "\n" in location:
        location = location.split("\n")[0].strip()
    
    return location

def geocode(location):
    if location is None:
        print(f"跳过无效位置")
        return [0, 0]
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location,
        "key": GOOGLE_API_KEY
    }
    
    try:
        print(f"尝试位置: {location}")
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data["status"] == "OK":
            result = data["results"][0]
            location = result["geometry"]["location"]
            coords = [location["lng"], location["lat"]]
            print(f"✓ 找到坐标: {coords}")
            return coords
        else:
            print(f"× API 返回错误: {data.get('status', 'UNKNOWN_ERROR')}")
    except Exception as e:
        print(f"处理位置时出错: {str(e)}")
    
    print("× 无法找到位置")
    return [0, 0]

if not GOOGLE_API_KEY:
    print("错误：未找到 GOOGLE_API_KEY 环境变量")
    exit(1)

print("开始读取位置数据...")
# 读取带有位置信息的数据
df = pd.read_csv("data_with_loc.csv", index_col=0)
print(f"读取了 {len(df)} 个视频的数据")

# 清理位置数据
print("\n清理位置数据...")
df["location"] = df["location"].apply(clean_location)

# 初始化 geocode 列
df["geocode"] = None

print("\n开始地理编码...")
# 对每个位置进行地理编码
total = len(df)
for idx, row in df.iterrows():
    print(f"\n处理 {idx + 1}/{total}: {row.get('location', 'N/A')}")
    coords = geocode(row["location"])
    df.loc[idx, "geocode"] = str(coords)
    time.sleep(0.1)  # 避免超过 API 限制

print("\n保存结果...")
# 保存结果
df.to_csv("3_geocoded.csv")

# 打印统计信息
successful = df[df["geocode"].apply(lambda x: eval(x) != [0, 0])].shape[0]
print(f"\n地理编码完成！")
print(f"总计处理: {total} 个位置")
print(f"成功获取: {successful} 个坐标")
print(f"无法获取: {total - successful} 个坐标") 