# %%
import pandas as pd
import sys

# %%
try:
    df = pd.read_csv("data.csv", index_col=0)
    print(f"Successfully loaded {len(df)} videos from data.csv")
except FileNotFoundError:
    print("Error: data.csv not found. Please run 1_gather_data.py first.")
    sys.exit(1)
except Exception as e:
    print(f"Error loading data.csv: {str(e)}")
    sys.exit(1)

# %%
from openai import OpenAI
from dotenv import load_dotenv
import os

try:
    load_dotenv(".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    client = OpenAI(api_key=api_key)
    print("Successfully initialized OpenAI client")
except Exception as e:
    print(f"Error initializing OpenAI client: {str(e)}")
    sys.exit(1)

# %%
def get_location(row):
    try:
        print(f"Processing video: {row['title'][:50]}...")
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "given a video description and title, give the location that the video was filmed.\
                  If it's not extremely clear, say \"no location found\" all lowercase with no punctuation. \
                 get as specific of a location as possible with the given inputs. \
                    Especially if there is a bulilding named in the description, this should be the response.\
                 Ideally, output should be formatted 'location, city, state, country' if applicable. If not applicable, just skip"},
                {
                    "role": "user",
                    "content": f'title: "{row["title"]}", description:"{row["description"]}"'
                }
            ]
        )
        location = completion.choices[0].message.content
        print(f"Found location: {location}")
        return location
    except Exception as e:
        print(f"Error processing video {row['title'][:50]}: {str(e)}")
        return "no location found"

print(f"\nStarting to process {len(df)} videos...")
responses = df.apply(get_location, axis=1)

# %%
df["location"] = responses
print(f"\nFinished processing all videos. Found {len(df[df['location'] != 'no location found'])} locations.")

# %%
try:
    df.to_csv("data_with_loc.csv")
    print("Successfully saved results to data_with_loc.csv")
except Exception as e:
    print(f"Error saving results: {str(e)}")
    sys.exit(1)


