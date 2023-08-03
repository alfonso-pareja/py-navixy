from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timedelta
import math
import uvicorn
import requests
import copy

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
HASH_API = '616c1befc270f3e662ae1cb0df89d030'
AVERAGE_SPEED_KPH = 47

@app.get("/")
def read_root():
    return "Hello World"


@app.get("/v1/alerts")
def bi_servicev1(dateFrom: Optional[str] = None, dateTo: Optional[str] = None, hash: str = Query(...)):
    global HASH_API
    HASH_API = hash

    list_data = get_alerts_list()
    return list_data;
    

@app.get('/mock/bi')
def mock_bi_service():

    fecha_hora_actual = datetime.now()
    fecha_hora_formateada = fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S")

    return [
        {
            "estimated_time": '7h 15m',
            "estimated_time_arrival": '0m',
            "route_name": 'Ruta de Prueba Arribo City',
            "vehicle_registration": 'HYDJ34',
            "destination_route_name": 'PARADA FINAL Pasada Daemon Travel',
            "task_name": 'Despacho de transporte Bonito',
            "state": 'Arribado',
            "date": fecha_hora_formateada
        },
        {
            "estimated_time": '4h 25m',
            "estimated_time_arrival": '1h 25m',
            "route_name": 'Ruta de Prueba Daemon Travel',
            "vehicle_registration": 'ETEB93',
            "destination_route_name": 'PARADA FINAL Crazy City',
            "task_name": 'Despacho de transporte Bonito',
            "state": 'Iniciada',
            "date": fecha_hora_formateada
        },
        {
            "estimated_time": '4h 45m',
            "estimated_time_arrival": '1h 55m',
            "route_name": 'Ruta de Prueba Los Angeles Bitch',
            "vehicle_registration": 'UIEY32',
            "destination_route_name": 'PARADA FINALNormal City',
            "task_name": 'Despacho de transporte Bonito',
            "state": 'Transito',
            "date": fecha_hora_formateada
        },
        {
            "estimated_time": '5h 30m',
            "estimated_time_arrival": '2h 20m',
            "route_name": 'Ruta de Prueba Hight way to Heaven',
            "vehicle_registration": 'HDHE32',
            "destination_route_name": 'PARADA FINAL I DONT KNOW WHAT NAME PUT HERE.',
            "task_name": 'Despacho de transporte Bonito',
            "state": 'Iniciada',
            "date": fecha_hora_formateada
        }
    ]  


# @app.get("/bi")
# def bi_service(dateFrom: Optional[str] = None, dateTo: Optional[str] = None, hash: str = Query(...)):
#     global HASH_API
#     HASH_API = hash

#     filtered_data = get_task_list(dateFrom, dateTo)
#     return filtered_data

# @app.get("/view/bi")
# def view_bi(request: Request, dateFrom: Optional[str] = None, dateTo: Optional[str] = None, hash: str = Query(...)):
#     global HASH_API
#     HASH_API = hash

#     filtered_data = get_task_list(dateFrom, dateTo)
#     return templates.TemplateResponse("bi.html", {"request": request, "data": filtered_data})



## /////// ------ ///////
@app.get("/v1/navixy")
def get_info_navixy():
    


    return build_navixy()



## Armar respuesta
def build_navixy():
    trackers = get_tracker_list_filtered()
    task_list = get_trackers_task_list()

    formatted_response = []
    for task in task_list:
        tracker = [track for track in trackers if track["id"] == task["tracker_id"]]
        # return [{"id": item["id"], "label": item["label"]} for item in data["list"]]

        start_lat = task["checkpoint_start"]["lat"]
        start_lng = task["checkpoint_start"]["lng"]
        end_lat   = task["checkpoint_end"]["lat"]
        end_lng   = task["checkpoint_end"]["lng"]

        track_location = get_tracker_location(task["tracker_id"])
        current_lat = track_location["track_location_lat"]
        current_lng = track_location["track_location_lng"]

        task_status = calculate_task_status(task, current_lat, current_lng)

        if task_status == 'Arribado':
            time_to_arribe = time_diff(task["checkpoint_end"])
            if(time_to_arribe is False): 
                formatted_task = {
                    "estimated_time": calculate_total_time_estimation(task["checkpoints"]),
                    "estimated_time_arrival": calculate_dynamic_distance_time(current_lat, current_lng,  task["checkpoints"])[1],
                    "initial_route_name": task["checkpoint_start"]["label"],
                    "destination_route_name": task["checkpoint_end"]["label"],
                    "route_name": task["route_name"],
                    "tracker_location_lat": current_lat,
                    "tracker_location_lng": current_lng,
                    "tracker_device_movement": track_location["tracker_device_movement"],
                    "tracker_label": None,
                    "tracker_speed": track_location["tracker_speed"],
                    "task_name": task["route_name"],
                    "state": calculate_task_status(task, current_lat, current_lng),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        else:
            formatted_task = {
                "estimated_time": calculate_total_time_estimation(task["checkpoints"]),
                "estimated_time_arrival": calculate_dynamic_distance_time(current_lat, current_lng,  task["checkpoints"])[1],
                "initial_route_name": task["checkpoint_start"]["label"],
                "destination_route_name": task["checkpoint_end"]["label"],
                "route_name": task["route_name"],
                "tracker_location_lat": current_lat,
                "tracker_location_lng": current_lng,
                "tracker_device_movement": track_location["tracker_device_movement"],
                "tracker_label": None,
                "tracker_speed": track_location["tracker_speed"],
                "task_name": task["route_name"],
                "state": calculate_task_status(task, current_lat, current_lng),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        formatted_response.append(formatted_task)

    return formatted_response


def time_diff(arrival_date_str):
    # Convertir la cadena en un objeto de fecha y hora
    arrival_date = datetime.strptime(arrival_date_str, "%Y-%m-%d %H:%M:%S")

    # Obtener la hora actual
    current_time = datetime.now()

    # Calcular la diferencia de tiempo entre la fecha de llegada y la hora actual
    time_diff = current_time - arrival_date

    # Verificar si han pasado más de 15 minutos desde la llegada
    if time_diff > timedelta(minutes=15):
        return True
    else:
        return False


def calculate_task_status(task, current_lat, current_lng):
    if task["checkpoint_end"]["status"] == "done":
        return "Arribado"

    estimated_time_to_first = calculate_time_estimation(task["checkpoint_start"]["lat"], task["checkpoint_start"]["lng"], current_lat, current_lng) 
    if (estimated_time_to_first[1] >= 30) :
        return "Transito"

    if task["checkpoint_start"]["status"] == "done":
        return "Inciada"
    
   

## Tracker List
def get_tracker_list_filtered():
    url = f"{BASE_URL}/tracker/list?hash={HASH_API}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return [{"id": item["id"], "label": item["label"]} for item in data["list"]]

    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

## Localizacion
def get_tracker_location(trackerId):
    url = f"{BASE_URL}/tracker/get_state?tracker_id={trackerId}&hash={HASH_API}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "track_location_lat": data["state"]["gps"]["location"].get("lat", 0),
            "track_location_lng": data["state"]["gps"]["location"].get("lng", 0),
            "tracker_speed": data["state"]["gps"]["speed"],
            "tracker_device_status": data["state"]["connection_status"],
            "tracker_device_movement": data["state"]["movement_status"]
        }

    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

## Lista de tareas
def get_trackers_task_list():
    url = f"{BASE_URL}/task/list"
    body = {
        "from": "2023-08-02 00:00:00",
        "to": "2023-08-03 23:59:59",
        "types": [
            "route"
        ],
        "hash": HASH_API
    }
    response = requests.post(url, json=body)

    if response.status_code == 200:
        data = response.json()
        return [extract_data_task_list(item) for item in data["list"]]
    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

def extract_data_task_list(item):
    checkpoints_data = []
    for checkpoint in item["checkpoints"]:
        checkpoint_data = {
            "tracker_id": checkpoint["tracker_id"],
            "status": checkpoint["status"],
            "label": checkpoint["label"],
            "description": checkpoint["description"],
            "origin": checkpoint["origin"],
            "lat": checkpoint["location"]["lat"],
            "lng": checkpoint["location"]["lng"],
            "address": checkpoint["location"]["address"],
            "arrival_date": checkpoint["arrival_date"],
            "id": checkpoint["id"]
        }
        checkpoints_data.append(checkpoint_data)

    return {
        "checkpoints": checkpoints_data,
        "checkpoint_start": checkpoints_data[0] if checkpoints_data else None,
        "checkpoint_end": checkpoints_data[-1] if checkpoints_data else None,
        "tracker_id": item["tracker_id"],
        "status_task": item["status"],
        "status_label": status_text(item["status"]),
        "route_name": item["label"]
    }

def status_text(status):
    if status == "failed":
        return "no completado"
    elif status == "assigned":
        return "asignado"
    elif status == "done":
        return "completado"
    else:
        return status

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en kilómetros
    R = 6371.0

    # Convertir latitud y longitud de grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Diferencia entre latitudes y longitudes
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Fórmula del haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distancia en kilómetros
    distance = R * c
    return distance

def time_to_reach_destination(distance, average_speed):
    # Tiempo en horas
    time_in_hours = distance / average_speed
    return time_in_hours


def calculate_time_estimation(start_lat, start_lng, end_lat, end_lng):
    # Calcular la distancia entre las ubicaciones de inicio y fin de la tarea en kilómetros
    distance_between_points = haversine_distance(start_lat, start_lng, end_lat, end_lng)

    # Calcular el tiempo estimado de la tarea en horas
    estimated_time_hours = time_to_reach_destination(distance_between_points, AVERAGE_SPEED_KPH)

    # Formatear el tiempo estimado en horas y minutos
    hours = int(estimated_time_hours)
    minutes = int((estimated_time_hours - hours) * 60)

    # Agregar el tiempo estimado a la tarea
    estimated_time = f"{hours}h {minutes}m"
    estimated_minutes = hours * 60 + minutes

    return estimated_time, estimated_minutes

def calculate_total_time_estimation(checkpoints):
    total_distance = 0

    for i in range(len(checkpoints) - 1):
        start_checkpoint = checkpoints[i]
        end_checkpoint = checkpoints[i + 1]
        start_lat = start_checkpoint["lat"]
        start_lng = start_checkpoint["lng"]
        end_lat = end_checkpoint["lat"]
        end_lng = end_checkpoint["lng"]

        # Calcular la distancia entre las ubicaciones de inicio y fin de la tarea en kilómetros
        distance_between_points = haversine_distance(start_lat, start_lng, end_lat, end_lng)

        # Acumular la distancia total
        total_distance += distance_between_points

    # Calcular el tiempo estimado de la ruta completa en horas
    estimated_time_hours = time_to_reach_destination(total_distance, AVERAGE_SPEED_KPH)

    # Formatear el tiempo estimado en horas y minutos
    hours = int(estimated_time_hours)
    minutes = int((estimated_time_hours - hours) * 60)

    return f"{hours}h {minutes}m"

# def calculate_distance_to_next_checkpoint(current_lat, current_lng, next_checkpoint):
#     next_lat = next_checkpoint["lat"]
#     next_lng = next_checkpoint["lng"]
#     distance_to_next_checkpoint = haversine_distance(current_lat, current_lng, next_lat, next_lng)
#     return distance_to_next_checkpoint

def format_time1(days, hours, minutes):
    formatted_time = ""
    if days > 0:
        formatted_time += f"{int(days)}d "
    if hours > 0:
        formatted_time += f"{int(hours)}h "
    formatted_time += f"{int(minutes)}m"
    return formatted_time

def calculate_dynamic_distance_time(current_lat, current_lng, checkpoints):
    total_distance = 0
    total_time_in_minutes = 0

    # Encuentra el índice del siguiente punto no completado (que aún no ha sido visitado)
    next_uncompleted_index = -1
    for index, checkpoint in enumerate(checkpoints):
        if checkpoint["status"] != "done":
            next_uncompleted_index = index
            break

    # Si se encontró un siguiente punto no completado
    if next_uncompleted_index != -1:
        # Calcula la distancia y el tiempo estimado desde la ubicación actual hasta ese punto no completado
        next_checkpoint = checkpoints[next_uncompleted_index]
        checkpoint_lat = next_checkpoint["lat"]
        checkpoint_lng = next_checkpoint["lng"]
        distance_to_next_checkpoint = haversine_distance(current_lat, current_lng, checkpoint_lat, checkpoint_lng)
        time_to_next_checkpoint = time_to_reach_destination(distance_to_next_checkpoint, AVERAGE_SPEED_KPH)

        total_distance += distance_to_next_checkpoint
        total_time_in_minutes += time_to_next_checkpoint * 60

        # Actualiza la ubicación actual con la ubicación del siguiente punto no completado
        current_lat = checkpoint_lat
        current_lng = checkpoint_lng

    # Repite el proceso para el siguiente punto no completado (Punto D)
    # Si hay un siguiente punto no completado, se calculará la distancia y el tiempo estimado desde la ubicación actual
    # hasta ese punto no completado, y se actualizará la ubicación actual.
    # Continuará hasta que se haya visitado todos los puntos o no haya más puntos no completados.

    # Convierte el tiempo total de minutos a días, horas y minutos
    days, remainder = divmod(total_time_in_minutes, 24 * 60)
    hours, minutes = divmod(remainder, 60)

    formatted_time = format_time1(days, hours, minutes)

    return total_distance, formatted_time






## /////// ------ ///////




## Alert List
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
        localizaciones = [{ "patente": item["extra"]["tracker_label"], "location_lat": item["location"]["lat"], "location_lng": item["location"]["lng"], "location_address": item["location"]["address"] } for item in data["list"]]


        return {
            "alarm_list": alarmas,
            "plate_list": patentes_ordenadas,
            "plate_count_list": recuento_ordenado,
            "plate_location_list": localizaciones
        }
    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")




## OLD

# def get_task_list(dateFrom=None, dateTo=None):
#     url = f"{BASE_URL}/task/list"

#     payload = {
#         "trackers": [],
#         "from": "",
#         "to": "",
#         "types": [
#             "route",
#             "task"
#         ],
#         "limit": 51,
#         "offset": 0,
#         "sort": [
#             "to=desc"
#         ],
#         "hash": HASH_API
#     }

#     if dateFrom is not None:
#         payload["from"] = dateFrom
#     else:
#         # Calcular fecha actual menos un mes
#         last_month = datetime.now() - timedelta(days=30)
#         payload["from"] = last_month.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

#     if dateTo is not None:
#         payload["to"] = dateTo
#     else:
#         # Calcular fecha actual
#         payload["to"] = datetime.now().replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")


#     response = requests.post(url, json=payload)

#     if response.status_code == 200:
#         data = response.json()
#         filtered_data = filter_data(data)
#         return filtered_data
#     else:
#         return {"error": "Failed to fetch data"}

# def filter_data(data):
#     filtered_list = []
#     all_devices_list = get_tracker_list()


#     for item in data["list"]:
#         if item["status"] == "assigned":
#             filtered_item = {
#                 "id": item["id"],
#                 "estado_tarea": item["status"],
#                 "nombre_ruta": item["label"],
#                 "tracker_id":  item["tracker_id"],
#                 "checkpoint_ids": item["checkpoint_ids"],
#                 "patente": [device["label"] for device in all_devices_list if device["id"] == item["tracker_id"]],
#                 "checkpoints": [],
#                 "tracker": {}
#             }
#             for checkpoint in item["checkpoints"]:
#                 if checkpoint["status"] == "assigned":
#                     filtered_item["checkpoints"].append({
#                         "id": checkpoint["id"],
#                         "tracker_id": checkpoint["tracker_id"],
#                         "status": checkpoint["status"],
#                         "checkpoint_nombre": checkpoint["label"],
#                         "location": checkpoint["location"],
#                         "fecha_llegada": checkpoint["arrival_date"],
#                         "duracion_parada": checkpoint["stay_duration"],
#                         "min_stay_duration": checkpoint["min_stay_duration"],
#                         "min_arrival_duration": checkpoint["min_arrival_duration"],
#                     })


#             filtered_item["tracker"] = get_info_tracker(filtered_item["tracker_id"])
#             filtered_list.append(filtered_item)

#     return {
#         "list": filtered_list,
#         "count": len(filtered_list),
#         "success": True
#     }

# def get_info_tracker(tracker_id):
#     url = f"{BASE_URL}/tracker/get_state?tracker_id={tracker_id}&hash={HASH_API}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = (response.json())["state"]
#     else:
#         return {"error": "Failed to fetch data"}


#     return {
#         "id": tracker_id,
#         "location": data["gps"]["location"],
#         "gps": data["gps"],
#         "connection_status": data["connection_status"],
#         "movement_status": data["movement_status"],
#         "actual_track_update": data["actual_track_update"]
#     }

# def get_tracker_list():
#     url = f"{BASE_URL}/tracker/get_state?hash={HASH_API}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = (response.json())["list"]
#     else:
#         return []



# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)