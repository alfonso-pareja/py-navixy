from fastapi import FastAPI
from app.routes import router as app_router

app = FastAPI()

app.include_router(app_router)



# from fastapi import FastAPI, HTTPException
# from datetime import datetime, timedelta
# from geopy.distance import geodesic
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse

# from typing import Optional
# import pytz
# import math
# import requests

# app = FastAPI()
# templates = Jinja2Templates(directory="templates")

# BASE_URL           = 'https://apigps.fiordoaustral.com'
# HASH_API           = '75cbfbbfd16e4df04e890082f14335eb'
# AVERAGE_SPEED_KPH  = 47
# GOOGLEMAPS_API_KEY = 'AIzaSyA1rnpXPXbi_A0UC_2iMAZLAWbmYFvlri8'
# ACCOUNT_NAME       = 'victor@tecnobus.cl'
# ACCOUNT_PASS       = 'T3cn0Bus!2023'

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     return templates.TemplateResponse("bi.html", { "request": {}, "title": "HOla"})


# @app.get("/v1/navixy")
# def get_info_navixy(days: Optional[int] = None):
#     verifyToken()

#     return build_navixy(days)

# @app.get("/v1/navixy/alerts")
# def get_info_navixy(days: Optional[int] = None):
#     verifyToken()



# def verifyToken():
#     global HASH_API
#     # Realiza la consulta previa para verificar si el hash es válido
#     if not is_valid_hash(HASH_API):
#         # Si el hash no es válido, renueva el hash
#         HASH_API = renew_hash()

# def is_valid_hash(hash_value):
#     url = f"{BASE_URL}/tracker/readings/list?tracker_id=289&hash={hash_value}"
#     response = requests.get(url)
#     return response.status_code == 200

# def renew_hash():
#     global HASH_API
#     # Realiza la consulta para obtener un nuevo hash válido
#     url = f"{BASE_URL}/user/auth?login={ACCOUNT_NAME}&password={ACCOUNT_PASS}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         new_hash = data.get("hash")
#         if new_hash:
#             HASH_API = new_hash
#             return new_hash

#     # Si no se pudo obtener un nuevo hash, lanza una excepción o retorna el hash anterior
#     # Aquí se puede personalizar según lo que se prefiera hacer en caso de error.
#     raise HTTPException(status_code=500, detail="Failed to obtain a valid hash")



# def build_navixy(daysToGetInfo: Optional[int]):
#     trackers = get_tracker_list_filtered()
#     task_list = get_trackers_task_list(daysToGetInfo)

#     formatted_response = []
#     formatted_task = {}
#     for task in task_list:
#         tracker = [track for track in trackers if track["id"] == task["tracker_id"]]

#         first_check_lat  = task["checkpoint_start"]["lat"]
#         first_check_lng  = task["checkpoint_start"]["lng"]
#         last_check_lat   = task["checkpoint_end"]["lat"]
#         last_check_lng   = task["checkpoint_end"]["lng"]

#         track_location = get_tracker_location(task["tracker_id"])
#         current_lat    = track_location["track_location_lat"]
#         current_lng    = track_location["track_location_lng"]

#         current_location = f"{current_lat},{current_lng}"
#         end_location     = f"{last_check_lat},{last_check_lng}"


#         formatted_time = get_formatted_time()
#         task_status    = calculate_task_status(task, current_lat, current_lng)


#         formatted_task = {
#             "status": '',
#             "estimated_time": '',
#             "estimated_time_arrival": '',
#             "initial_route_name":       task["checkpoint_start"]["label"],
#             "destination_route_name":   task["checkpoint_end"]["label"],
#             "arrival_date_first_check": task["checkpoint_start"]["arrival_date"],
#             "arrival_date_last_check":  task["checkpoint_end"]["arrival_date"],
#             "firts_checkpoint_lat":     first_check_lat,
#             "firts_checkpoint_lng":     first_check_lng,
#             "end_checkpoint_lat":       last_check_lng,
#             "end_checkpoint_lng":       last_check_lng,
#             "route_name":               task["route_name"],
#             "tracker_location_lat":     current_lat,
#             "tracker_location_lng":     current_lng,
#             "tracker_device_movement":  track_location["tracker_device_movement"],
#             "tracker_label":            tracker[0]["label"],
#             "tracker_speed":            track_location["tracker_speed"],
#             "task_name":                task["route_name"],
#             "task_status":              task["status_task"],
#             "state":                    task_status,
#             "check_completed":          task["check_completed"],
#             "last_checkpoint":          task["last_checkpoint"],
#             "date":                     formatted_time
#         }


#         # Trackers ruta Finalizada
#         if task_status == 'Arribado':
#             ## Calcular el tiempo transcurrido tras la llegada, retorna True si pasaron mas de 15 minutos
#             timediff_to_arribe = time_diff(task["checkpoint_end"]["arrival_date"])

#             # Si transcurrieron mas de 15 minutos, se informa del tiempo
#             if timediff_to_arribe > timedelta(minutes=15):
#                 formatted_task['status']       =  "TERMINATED"
#                 formatted_task['Message']      =  f'{tracker[0]["label"]} Termino el recorrido y pasaron mas de 15 minutos'
#                 formatted_task['finished_ago'] = format_timedelta(timediff_to_arribe)
#                 formatted_task['estimated_time'] = "0h 0m"
#                 formatted_task['estimated_time_arrival'] = "0h 0m"

#             # Si aun no transcurren los 15 minutos, pero ya finalizo el recorrido
#             else:
#                 formatted_task['status'] = 'IN_PROGRESS'
#                 formatted_task['Message'] = f'{tracker[0]["label"]} Finalizo el recorrido hace {format_timedelta(timediff_to_arribe)}'
#                 formatted_task['estimated_time'] = get_distance_service(first_check_lat, first_check_lng, last_check_lat, last_check_lng)[1]
#                 formatted_task['estimated_time_arrival'] = get_distance_and_time(current_location, end_location)[1]
                
#         # Trackers en ruta
#         else:
#             formatted_task['status'] = 'IN_PROGRESS'
#             formatted_task['estimated_time'] = get_distance_service(first_check_lat, first_check_lng, last_check_lat, last_check_lng)[1]
#             formatted_task['estimated_time_arrival'] = get_distance_and_time(current_location, end_location)[1]


#             if task_status == 'Asignado' :
#                 formatted_task['Message'] = f'{tracker[0]["label"]} Aun no ingresa al primer Checkpoint'

#             if task_status == 'Transito':
#                 formatted_task['Message'] = f'{tracker[0]["label"]} ha completado {formatted_task["check_completed"]} Checkpoints. Ultimo Checkpoint {formatted_task["last_checkpoint"]}'

#             # Iniciada
#             else:
#                 formatted_task['Message'] = f'{tracker[0]["label"]} Inicio la ruta.'

#         if formatted_task:
#             formatted_response.append(formatted_task)


#     sorted_response = sorted(formatted_response, key=status_sort_key)
#     return sorted_response

# def get_formatted_time():
#     local_now = datetime.now()
#     santiago_timezone = pytz.timezone('America/Santiago')
#     santiago_now = local_now.astimezone(santiago_timezone)
#     formatted_time = santiago_now.strftime("%Y-%m-%d %H:%M:%S")
#     return formatted_time

# def calculate_task_status(task, current_lat, current_lng):
#     if task["checkpoint_end"]["status"] == "done":
#         return "Arribado"
    
#     if task["checkpoint_start"]["status"] == "done":
#         estimated_time_to_first = calculate_time_estimation(task["checkpoint_start"]["lat"], task["checkpoint_start"]["lng"], current_lat, current_lng) 
#         if (estimated_time_to_first[1] >= 30) :
#             return "Transito"
#         return "Iniciada"
    
#     return 'Asignado'
   
# def status_sort_key(task):
#     status_order = {
#         "assigned": 0,
#         "done": 1,
#         "failed": 2
#     }
#     return status_order.get(task["task_status"], 99)

# def get_tracker_location(trackerId):
#     url = f"{BASE_URL}/tracker/get_state?tracker_id={trackerId}&hash={HASH_API}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         return {
#             "track_location_lat": data["state"]["gps"]["location"].get("lat", 0),
#             "track_location_lng": data["state"]["gps"]["location"].get("lng", 0),
#             "tracker_speed": data["state"]["gps"]["speed"],
#             "tracker_device_status": data["state"]["connection_status"],
#             "tracker_device_movement": data["state"]["movement_status"]
#         }
#     else:
#         print("Error:")
#         raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

# def get_tracker_list_filtered():
#     url = f"{BASE_URL}/tracker/list?hash={HASH_API}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         return [{"id": item["id"], "label": item["label"]} for item in data["list"]]
#     else:
#         print("Error:")
#         raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

# def get_distance_service(start_lat, start_lng, end_lat, end_lng):
#     url = f"{BASE_URL}/route/get"
#     body = {
#         "pgk": "",
#         "start": {
#             "lat": start_lat,
#             "lng": start_lng
#         },
#         "end": {
#             "lat": end_lat,
#             "lng": end_lng
#         },
#         "waypoints": [],
#         "provider_type": "osrm",
#         "point_limit": 512,
#         "hash": HASH_API
#     }

#     response = requests.post(url, json=body)
#     if response.status_code == 200:
#         data = response.json()
#         result = data["key_points"][1]
#         return meters_to_kilometers(result["distance"]), format_time(result["time"])
#     else:
#         raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

# def get_trackers_task_list(daysToGetInfo: Optional[int]):
#     daysToGetInfo = 1 if daysToGetInfo is None else daysToGetInfo
#     current_date  = datetime.now()
#     tomorrow_date = current_date + timedelta(days=1)
#     from_date_str = (current_date - timedelta(days=daysToGetInfo)).strftime("%Y-%m-%d 23:59:59")
#     to_date_str   = tomorrow_date.strftime("%Y-%m-%d 23:59:59")

#     body = {
#         "from": from_date_str,
#         "to": to_date_str,
#         "types": ["route"],
        
#         "hash": HASH_API
#     }


#     url = f"{BASE_URL}/task/list"
#     response = requests.post(url, json=body)

#     if response.status_code == 200:
#         data = response.json()
#         return [extract_data_task_list(item) for item in data["list"]]
#     else:
#         print("Error:")
#         raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

# def extract_data_task_list(item):
#     checkpoints_data = []
#     for checkpoint in item["checkpoints"]:
#         checkpoint_data = {
#             "tracker_id":   checkpoint["tracker_id"],
#             "status":       checkpoint["status"],
#             "label":        checkpoint["label"],
#             "description":  checkpoint["description"],
#             "origin":       checkpoint["origin"],
#             "lat":          checkpoint["location"]["lat"],
#             "lng":          checkpoint["location"]["lng"],
#             "address":      checkpoint["location"]["address"],
#             "arrival_date": checkpoint["arrival_date"],
#             "id":           checkpoint["id"]
#         }
#         checkpoints_data.append(checkpoint_data)

#     completed_checkpoints = sum(1 for checkpoint in checkpoints_data if checkpoint["arrival_date"] is not None)
#     total_checkpoints     = len(checkpoints_data)

#     index_checkpoint = completed_checkpoints-1
#     return {
#         "checkpoints":      checkpoints_data,
#         "check_completed":   f"{completed_checkpoints}/{total_checkpoints}",
#         "last_checkpoint":  checkpoints_data[index_checkpoint]["label"] if 0 <= index_checkpoint < len(checkpoints_data) else '',
#         "checkpoint_start": checkpoints_data[0] if checkpoints_data else None,
#         "checkpoint_end":   checkpoints_data[-1] if checkpoints_data else None,
#         "tracker_id":       item["tracker_id"],
#         "status_task":      item["status"],
#         "status_label":     status_text(item["status"]),
#         "route_name":       item["label"]
#     }

# def meters_to_kilometers(meters):
#     return meters / 1000

# def calculate_time_estimation(start_lat, start_lng, end_lat, end_lng):
#     distance_between_points = haversine_distance(start_lat, start_lng, end_lat, end_lng)
#     estimated_time_hours = time_to_reach_destination(distance_between_points, AVERAGE_SPEED_KPH)
#     hours = int(estimated_time_hours)
#     minutes = int((estimated_time_hours - hours) * 60)
#     estimated_time = f"{hours}h {minutes}m"
#     estimated_minutes = hours * 60 + minutes
#     return estimated_time, estimated_minutes

# def haversine_distance(lat1, lon1, lat2, lon2):
#     # Radio de la Tierra en kilómetros
#     R = 6371.0
#     lat1_rad = math.radians(lat1)
#     lon1_rad = math.radians(lon1)
#     lat2_rad = math.radians(lat2)
#     lon2_rad = math.radians(lon2)
#     dlat = lat2_rad - lat1_rad
#     dlon = lon2_rad - lon1_rad
#     a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     distance = R * c
#     return distance

# def time_to_reach_destination(distance, average_speed):
#     time_in_hours = distance / average_speed
#     return time_in_hours

# def calculate_dynamic_distance_time(current_lat, current_lng, checkpoints):
#     total_distance = 0
#     total_time_in_minutes = 0

#     current_location = f"{current_lat},{current_lng}"

#     # Encuentra el índice del siguiente punto no completado (que aún no ha sido visitado)
#     next_uncompleted_index = -1
#     for index, checkpoint in enumerate(checkpoints):
#         if checkpoint["status"] != "done":
#             next_uncompleted_index = index
#             break

#     # Si se encontró un siguiente punto no completado
#     if next_uncompleted_index != -1:
#         # Calcula la distancia y el tiempo estimado desde la ubicación actual hasta ese punto no completado
#         next_checkpoint = checkpoints[next_uncompleted_index]
#         checkpoint_lat = next_checkpoint["lat"]
#         checkpoint_lng = next_checkpoint["lng"]

#         end_location = f"{checkpoint_lat},{checkpoint_lng}"

#         distance_to_next_checkpoint = get_distance_and_time(current_location, end_location)[0],
#         distance = distance_to_next_checkpoint[0]

#         # distance_to_next_checkpoint = haversine_distance(current_lat, current_lng, checkpoint_lat, checkpoint_lng)
#         time_to_next_checkpoint = time_to_reach_destination(distance, AVERAGE_SPEED_KPH)

#         total_distance += distance
#         total_time_in_minutes += time_to_next_checkpoint * 60

#         # Actualiza la ubicación actual con la ubicación del siguiente punto no completado
#         current_lat = checkpoint_lat
#         current_lng = checkpoint_lng

#     # Repite el proceso para el siguiente punto no completado (Punto D)
#     # Si hay un siguiente punto no completado, se calculará la distancia y el tiempo estimado desde la ubicación actual
#     # hasta ese punto no completado, y se actualizará la ubicación actual.
#     # Continuará hasta que se haya visitado todos los puntos o no haya más puntos no completados.

#     # Convierte el tiempo total de minutos a días, horas y minutos
#     days, remainder = divmod(total_time_in_minutes, 24 * 60)
#     hours, minutes = divmod(remainder, 60)

#     formatted_time = format_time1(days, hours, minutes)

#     return total_distance, formatted_time

# def get_distance_and_time(origin, destination):
#     base_url = "https://maps.googleapis.com/maps/api/directions/json"
#     params = {
#         "origin": origin,
#         "destination": destination,
#         "key": GOOGLEMAPS_API_KEY,
#     }

#     response = requests.get(base_url, params=params)
#     data = response.json()

#     if data["status"] == "OK" and len(data["routes"]) > 0:
#         distance_in_meters = data["routes"][0]["legs"][0]["distance"]["value"]
#         # distance_in_kilometers = distance_in_meters / 1000

#         duration_in_seconds = data["routes"][0]["legs"][0]["duration"]["value"]
#         duration_formatted = format_time(duration_in_seconds)

#         return distance_in_meters, duration_formatted
#     else:
#         return None, None

# def status_text(status):
#     if status == "failed":
#         return "no completado"
#     elif status == "assigned":
#         return "asignado"
#     elif status == "done":
#         return "completado"
#     else:
#         return status

# def format_time_minutes(minutes):
#     hours = minutes // 60
#     minutes %= 60

#     if hours == 0:
#         return f"{int(minutes)}m"
#     elif minutes == 0:
#         return f"{int(hours)}h"
#     else:
#         return f"{int(hours)}h {(minutes)}m"

# def format_time(seconds):
#     hours = seconds // 3600
#     remaining_seconds = seconds % 3600
#     minutes = remaining_seconds // 60
#     return f"{hours}h {minutes}m"

# def format_time1(days, hours, minutes):
#     formatted_time = ""
#     if days > 0:
#         formatted_time += f"{int(days)}d "
#     if hours > 0:
#         formatted_time += f"{int(hours)}h "
#     formatted_time += f"{int(minutes)}m"
#     return formatted_time

# def format_timedelta(td):
#     # Calcular el total de segundos en el timedelta
#     total_seconds = td.total_seconds()

#     # Calcular horas y minutos
#     hours = int(total_seconds // 3600)
#     minutes = int((total_seconds % 3600) // 60)

#     return f"{hours}h {minutes}m"

# def time_diff(arrival_date_str):
#     # Convertir la cadena en un objeto de fecha y hora
#     arrival_date = datetime.strptime(arrival_date_str, "%Y-%m-%d %H:%M:%S")

#     # Obtener la hora actual
#     current_time = datetime.now()

#     # Calcular la diferencia de tiempo entre la fecha de llegada y la hora actual
#     time_diff = current_time - arrival_date

#     return time_diff

