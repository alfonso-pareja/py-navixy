
from typing import Optional
from config import Config
import requests


BASE_URL = Config.BASE_URL
HASH_API = Config.HASH_API

def get_alerts(dateFrom: str, dateTo: str, tracker: Optional[int]):
    body = {
        "from": dateFrom,
        "to": dateTo,
        "hash": HASH_API
    }
    if(tracker is not None):
        body["trackers"] = [tracker]

    
    url = f"{BASE_URL}/history/tracker/list"
    response = requests.post(url, json=body)

    if response.status_code == 200:
        data = response.json()
        return [extract_data_list(item) for item in data["list"]]
    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")



def extract_data_list(item):
    print(item)
    if(item is None): 
        return []

    return {
        "event": item["event"],
        "message": item["message"],
        "is_read": item["is_read"],
        "location_lat": item["location"]["lat"],
        "location_lng": item["location"]["lng"]
    }

