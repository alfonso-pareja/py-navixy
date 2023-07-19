from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timedelta
import uvicorn
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

templates = Jinja2Templates(directory="templates")

BASE_URL = 'https://apigps.fiordoaustral.com'
HASH_API = ''

@app.get("/")
def read_root():
    return "Hello World"


@app.get("/v1/bi")
def bi_servicev1(dateFrom: Optional[str] = None, dateTo: Optional[str] = None, hash: str = Query(...)):
    global HASH_API
    HASH_API = hash
    print("AQUI")

    list_data = get_alerts_list()
    return list_data;


@app.get("/bi")
def bi_service(dateFrom: Optional[str] = None, dateTo: Optional[str] = None, hash: str = Query(...)):
    global HASH_API
    HASH_API = hash

    filtered_data = get_task_list(dateFrom, dateTo)
    return filtered_data

@app.get("/view/bi")
def view_bi(request: Request, dateFrom: Optional[str] = None, dateTo: Optional[str] = None, hash: str = Query(...)):
    global HASH_API
    HASH_API = hash

    filtered_data = get_task_list(dateFrom, dateTo)
    return templates.TemplateResponse("bi.html", {"request": request, "data": filtered_data})



def get_alerts_list():
    url = f"{BASE_URL}/history/unread/list?hash={HASH_API}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        alarmas = [item["message"] for item in data["list"]]
        patentes = list(set(item["extra"]["tracker_label"] for item in data["list"]))
        recuento_patentes = [{ "patente": patente, "cantidad": sum(1 for item in data["list"] if item["extra"]["tracker_label"] == patente)} for patente in patentes]
        patentes_ordenadas = sorted(patentes, key=lambda x: next((item["cantidad"] for item in recuento_patentes if item["patente"] == x), 0), reverse=True)
        recuento_ordenado = sorted(recuento_patentes, key=lambda x: x["cantidad"], reverse=True)
        localizaciones = [{ "patente": item["extra"]["tracker_label"], "location": item["location"] } for item in data["list"]]


        return {
            "alarm_list": alarmas,
            "plate_list": patentes_ordenadas,
            "plate_count_list": recuento_ordenado,
            "plate_location_list": localizaciones
        }
    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")





def get_task_list(dateFrom=None, dateTo=None):
    url = f"{BASE_URL}/task/list"

    payload = {
        "trackers": [],
        "from": "",
        "to": "",
        "types": [
            "route",
            "task"
        ],
        "limit": 51,
        "offset": 0,
        "sort": [
            "to=desc"
        ],
        "hash": HASH_API
    }

    if dateFrom is not None:
        payload["from"] = dateFrom
    else:
        # Calcular fecha actual menos un mes
        last_month = datetime.now() - timedelta(days=30)
        payload["from"] = last_month.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

    if dateTo is not None:
        payload["to"] = dateTo
    else:
        # Calcular fecha actual
        payload["to"] = datetime.now().replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")


    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        filtered_data = filter_data(data)
        return filtered_data
    else:
        return {"error": "Failed to fetch data"}

def filter_data(data):
    filtered_list = []
    all_devices_list = get_tracker_list()


    for item in data["list"]:
        if item["status"] == "assigned":
            filtered_item = {
                "id": item["id"],
                "estado_tarea": item["status"],
                "nombre_ruta": item["label"],
                "tracker_id":  item["tracker_id"],
                "checkpoint_ids": item["checkpoint_ids"],
                "patente": [device["label"] for device in all_devices_list if device["id"] == item["tracker_id"]],
                "checkpoints": [],
                "tracker": {}
            }
            for checkpoint in item["checkpoints"]:
                if checkpoint["status"] == "assigned":
                    filtered_item["checkpoints"].append({
                        "id": checkpoint["id"],
                        "tracker_id": checkpoint["tracker_id"],
                        "status": checkpoint["status"],
                        "checkpoint_nombre": checkpoint["label"],
                        "location": checkpoint["location"],
                        "fecha_llegada": checkpoint["arrival_date"],
                        "duracion_parada": checkpoint["stay_duration"],
                        "min_stay_duration": checkpoint["min_stay_duration"],
                        "min_arrival_duration": checkpoint["min_arrival_duration"],
                    })


            filtered_item["tracker"] = get_info_tracker(filtered_item["tracker_id"])
            filtered_list.append(filtered_item)

    return {
        "list": filtered_list,
        "count": len(filtered_list),
        "success": True
    }


def get_info_tracker(tracker_id):
    url = f"{BASE_URL}/tracker/get_state?tracker_id={tracker_id}&hash={HASH_API}"
    response = requests.get(url)
    if response.status_code == 200:
        data = (response.json())["state"]
    else:
        return {"error": "Failed to fetch data"}


    return {
        "id": tracker_id,
        "location": data["gps"]["location"],
        "gps": data["gps"],
        "connection_status": data["connection_status"],
        "movement_status": data["movement_status"],
        "actual_track_update": data["actual_track_update"]
    }


def get_tracker_list():
    url = f"{BASE_URL}/tracker/get_state?hash={HASH_API}"
    response = requests.get(url)
    if response.status_code == 200:
        data = (response.json())["list"]
    else:
        return []



# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)