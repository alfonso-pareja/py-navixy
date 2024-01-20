import requests
from app.utils.reader import JsonReader
from app.utils.writer import JsonWriter

class Config:
    BASE_URL = 'https://apigps.fiordoaustral.com'
    HASH_API = JsonReader.get_json("./token.json").get("HASH_KEY")
    # HASH_API = '75cbfbbfd16e4df04e890082f14335eb'
    AVERAGE_SPEED_KPH = 47
    GOOGLEMAPS_API_KEY = 'c95840752944403e33649ced8c41a562'
    ACCOUNT_NAME = 'victor@tecnobus.cl'
    ACCOUNT_PASS = 'T3cn0Bus!2023'

    @staticmethod
    def verifyToken():
        if not Config.is_valid_hash(Config.HASH_API):
            new_key = Config.renew_hash()
            JsonWriter.write_json("./token.json", {"HASH_KEY": new_key})
            Config.HASH_API = new_key

    @staticmethod
    def is_valid_hash(hash_value):
        url = f"{Config.BASE_URL}/tracker/readings/list?tracker_id=289&hash={hash_value}"
        response = requests.get(url)
        return response.status_code == 200

    @staticmethod
    def renew_hash():
        url = f"{Config.BASE_URL}/user/auth?login={Config.ACCOUNT_NAME}&password={Config.ACCOUNT_PASS}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            new_hash = data.get("hash")
            if new_hash:
                Config.HASH_API = new_hash
                return new_hash

        raise HTTPException(status_code=500, detail="Failed to obtain a valid hash")
