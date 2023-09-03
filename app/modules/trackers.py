
from typing import Optional
from config import Config
import requests

BASE_URL = Config.BASE_URL
HASH_API = Config.HASH_API

def get_trackers():
    url = f"{BASE_URL}/tracker/list?hash={HASH_API}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return [{ "id": item["id"], "name": item["label"] } for item in data["list"]]

    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")
