import pandas as pd
import json
import ast

print("开始读取地理编码数据...")
# 读取数据
df = pd.read_csv("3_geocoded.csv", index_col=0)
print(f"读取了 {len(df)} 个视频的数据")

# 移除不需要的列
df = df.drop(columns=["description"])

# 处理地理编码数据
print("\n处理地理编码数据...")
def parse_geocode(geocode_str):
    try:
        # 将字符串形式的列表转换为实际的列表
        coords = ast.literal_eval(geocode_str)
        if coords == [0, 0]:
            return None
        return coords
    except:
        return None

df["geocode"] = df["geocode"].apply(parse_geocode)

# 移除没有地理位置的视频
df = df.dropna(subset=["geocode"])
print(f"处理后剩余 {len(df)} 个有效视频")

# 设置视频类型
print("\n根据标题设置视频类型...")
def get_video_type(title):
    title = title.lower()
    if "hiking" in title or "trek" in title or "trail" in title:
        return "hiking"
    elif any(word in title for word in ["days in", "life in", "trip to", "living in", "city"]):
        return "city"
    else:
        return "other"

df["playlist"] = df["title"].apply(get_video_type)

# 添加标记字段
df["marked"] = True

print("\n保存数据...")
# 保存为 JSON 供网页使用
web_data = df.to_dict(orient="records")
with open("../web/src/data/data.json", "w") as f:
    json.dump(web_data, f, ensure_ascii=False, indent=2)

print("数据已保存到 web/src/data/data.json")
print("数据处理完成！")