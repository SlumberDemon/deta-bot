import time
import requests
import requests
from thefuzz import fuzz

start_time = time.time()

data = requests.get(
    "https://api.github.com/repos/python-discord/bot/contents/bot/resources/tags"  # https://api.github.com/repos/slumberdemon/deta-bot/contents/resources/tags
).json()

items = []
for d in data:
    nr = fuzz.ratio(d["name"].replace(".md", ""), "a")
    nc = fuzz.ratio(requests.get(d["download_url"]).text.strip(), "a")
    if nr > 25 or nc > 50:
        if len(items) <= 25:
            items.append(
                {"name": d["name"].replace(".md", ""), "url": d["download_url"]}
            )

end_time = time.time()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")
# print(items)
