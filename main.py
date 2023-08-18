from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from geopy.distance import geodesic
import pytz
import math
import requests

app = FastAPI()

BASE_URL = 'https://apigps.fiordoaustral.com'
HASH_API = '7c06cc38ec9f36bd773dc79beb24a85d'
AVERAGE_SPEED_KPH = 47
GOOGLEMAPS_API_KEY = 'AIzaSyA1rnpXPXbi_A0UC_2iMAZLAWbmYFvlri8'

@app.get("/v1/navixy")
def get_info_navixy():
    global HASH_API
    # Realiza la consulta previa para verificar si el hash es válido
    if not is_valid_hash(HASH_API):
        # Si el hash no es válido, renueva el hash
        HASH_API = renew_hash()

    # Continúa con la función build_navixy()
    return build_navixy()


def is_valid_hash(hash_value):
    # Realiza la consulta para verificar si el hash es válido
    url = f"{BASE_URL}/tracker/readings/list?tracker_id=289&hash={hash_value}"
    response = requests.get(url)

    # Si la respuesta es 200, el hash es válido, de lo contrario, no lo es
    return response.status_code == 200

def renew_hash():
    global HASH_API
    # Realiza la consulta para obtener un nuevo hash válido
    url = f"{BASE_URL}/user/auth?login=victor@tecnobus.cl&password=T3cn0Bus!2023"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        new_hash = data.get("hash")
        if new_hash:
            HASH_API = new_hash
            return new_hash

    # Si no se pudo obtener un nuevo hash, lanza una excepción o retorna el hash anterior
    # Aquí se puede personalizar según lo que se prefiera hacer en caso de error.
    raise HTTPException(status_code=500, detail="Failed to obtain a valid hash")



def build_navixy():
    trackers = get_tracker_list_filtered()
    task_list = get_trackers_task_list()

    formatted_response = []
    formatted_task = {}
    for task in task_list:
        tracker = [track for track in trackers if track["id"] == task["tracker_id"]]
        local_now = datetime.now()
        santiago_timezone = pytz.timezone('America/Santiago')
        santiago_now = local_now.astimezone(santiago_timezone)
        formatted_time = santiago_now.strftime("%Y-%m-%d %H:%M:%S")

        start_lat = task["checkpoint_start"]["lat"]
        start_lng = task["checkpoint_start"]["lng"]
        end_lat = task["checkpoint_end"]["lat"]
        end_lng = task["checkpoint_end"]["lng"]

        track_location = get_tracker_location(task["tracker_id"])
        current_lat = track_location["track_location_lat"]
        current_lng = track_location["track_location_lng"]

        task_status = calculate_task_status(task, current_lat, current_lng)

        current_location = f"{current_lat},{current_lng}"
        end_location = f"{end_lat},{end_lng}"
        if task_status == 'Arribado':
            time_to_arribe = time_diff(task["checkpoint_end"]["arrival_date"])
            
            if time_to_arribe is False:
                formatted_task = {
                    "estimated_time": get_distance_service(start_lat, start_lng, end_lat, end_lng)[1],
                    "estimated_time_arrival": get_distance_and_time(current_location, end_location)[1],
                    "initial_route_name": task["checkpoint_start"]["label"],
                    "destination_route_name": task["checkpoint_end"]["label"],
                    "arrival_date_first_check": task["checkpoint_start"]["arrival_date"],
                    "arrival_date_last_check": task["checkpoint_end"]["arrival_date"],
                    "route_name": task["route_name"],
                    "tracker_location_lat": current_lat,
                    "tracker_location_lng": current_lng,
                    "tracker_device_movement": track_location["tracker_device_movement"],
                    "tracker_label":  tracker[0]["label"],
                    "tracker_speed": track_location["tracker_speed"],
                    "task_name": task["route_name"],
                    "task_status": task["status_task"],
                    "state": calculate_task_status(task, current_lat, current_lng),
                    "date": formatted_time

                }
            else:
                formatted_task = {
                    "status": "TERMINATED",
                    "tracker_label":  tracker[0]["label"],
                    "Message": f'{tracker[0]["label"]} Termino el recorrido y pasaron mas de 15 minutos',
                    "arrival_date_first_check": task["checkpoint_start"]["arrival_date"],
                    "arrival_date_last_check": task["checkpoint_end"]["arrival_date"],
                    "date": formatted_time,
                    "task_name": task["route_name"],
                    "task_status": task["status_task"],
                }
                print(f'{tracker[0]["label"]} Termino el recorrido y pasaron mas de 15 minutos')
        else:
      
            formatted_task = {
                "estimated_time": get_distance_service(start_lat, start_lng, end_lat, end_lng)[1],
                # "estimated_time_arrival_FROMSERVICE": calculate_dynamic_distance_time(current_lat, current_lng,  task["checkpoints"])[1],
                # "estimated_time_arrival_FROMACTUAL": get_distance_service(current_lat, current_lng,  end_lat, end_lng)[1],
                "estimated_time_arrival": get_distance_and_time(current_location, end_location)[1],
                "initial_route_name": task["checkpoint_start"]["label"],
                "destination_route_name": task["checkpoint_end"]["label"],
                "arrival_date_first_check": task["checkpoint_start"]["arrival_date"],
                "arrival_date_last_check": task["checkpoint_end"]["arrival_date"],

                "firts_checkpoint_lat": start_lat,
                "firts_checkpoint_lng": start_lng,
                "end_checkpoint_lat": end_lat,
                "end_checkpoint_lng": end_lng,

                "route_name": task["route_name"],
                "tracker_location_lat": current_lat,
                "tracker_location_lng": current_lng,
                "tracker_device_movement": track_location["tracker_device_movement"],
                "tracker_label":  tracker[0]["label"],
                "tracker_speed": track_location["tracker_speed"],
                "task_name": task["route_name"],
                "task_status": task["status_task"],
                "state": calculate_task_status(task, current_lat, current_lng),
                "date": formatted_time
            }

        if formatted_task:
            formatted_response.append(formatted_task)


    sorted_response = sorted(formatted_response, key=status_sort_key)
    return sorted_response


def calculate_task_status(task, current_lat, current_lng):
    if task["checkpoint_end"]["status"] == "done":
        return "Arribado"

    estimated_time_to_first = calculate_time_estimation(task["checkpoint_start"]["lat"], task["checkpoint_start"]["lng"], current_lat, current_lng) 
    if (estimated_time_to_first[1] >= 30) :
        return "Transito"

    if task["checkpoint_start"]["status"] == "done":
        return "Iniciada"
    
    return ''
   

def status_sort_key(task):
    status_order = {
        "assigned": 0,
        "done": 1,
        "failed": 2
    }
    return status_order.get(task["task_status"], 99)

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


def get_tracker_list_filtered():
    url = f"{BASE_URL}/tracker/list?hash={HASH_API}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return [{"id": item["id"], "label": item["label"]} for item in data["list"]]
    else:
        print("Error:")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")


def get_distance_service(start_lat, start_lng, end_lat, end_lng):
    url = f"{BASE_URL}/route/get"
    body = {
        "pgk": "",
        "start": {
            "lat": start_lat,
            "lng": start_lng
        },
        "end": {
            "lat": end_lat,
            "lng": end_lng
        },
        "waypoints": [],
        "provider_type": "osrm",
        "point_limit": 512,
        "hash": HASH_API
    }

    response = requests.post(url, json=body)
    if response.status_code == 200:
        data = response.json()
        result = data["key_points"][1]
        return meters_to_kilometers(result["distance"]), format_time(result["time"])
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")


def get_trackers_task_list():
    current_date = datetime.now()
    tomorrow_date = current_date + timedelta(days=1)
    from_date_str = current_date.strftime("%Y-%m-%d 00:00:00")
    to_date_str   = tomorrow_date.strftime("%Y-%m-%d 23:59:59")

    body = {
        "from": from_date_str,
        "to": to_date_str,
        "types": ["route"],
        
        "hash": HASH_API
    }

    url = f"{BASE_URL}/task/list"
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




def meters_to_kilometers(meters):
    return meters / 1000

def calculate_time_estimation(start_lat, start_lng, end_lat, end_lng):
    distance_between_points = haversine_distance(start_lat, start_lng, end_lat, end_lng)
    estimated_time_hours = time_to_reach_destination(distance_between_points, AVERAGE_SPEED_KPH)
    hours = int(estimated_time_hours)
    minutes = int((estimated_time_hours - hours) * 60)
    estimated_time = f"{hours}h {minutes}m"
    estimated_minutes = hours * 60 + minutes
    return estimated_time, estimated_minutes

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en kilómetros
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def time_to_reach_destination(distance, average_speed):
    time_in_hours = distance / average_speed
    return time_in_hours

def calculate_dynamic_distance_time(current_lat, current_lng, checkpoints):
    total_distance = 0
    total_time_in_minutes = 0

    current_location = f"{current_lat},{current_lng}"

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

        end_location = f"{checkpoint_lat},{checkpoint_lng}"

        distance_to_next_checkpoint = get_distance_and_time(current_location, end_location)[0],
        distance = distance_to_next_checkpoint[0]
        print(distance)
        # distance_to_next_checkpoint = haversine_distance(current_lat, current_lng, checkpoint_lat, checkpoint_lng)
        time_to_next_checkpoint = time_to_reach_destination(distance, AVERAGE_SPEED_KPH)

        total_distance += distance
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


# def calcular_distancia_tiempo_total(checkpoints, ubicacion_actual, velocidad_promedio):
#     coordenadas_checkpoints = {}
#     checkpoints_visitados = []
#     for checkpoint in checkpoints:
#         print(checkpoint)
#         nombre = str(checkpoint['id'])
#         latitud = checkpoint['lat']
#         longitud = checkpoint['lng']
#         coordenadas_checkpoints[nombre] = (latitud, longitud)
#         if checkpoint['status'] == 'done':
#             checkpoints_visitados.append(nombre)

#     # Encontrar los checkpoints no visitados (C y D)
#     checkpoints_no_visitados = [nombre for nombre in coordenadas_checkpoints if nombre not in checkpoints_visitados]

#     # Encontrar la distancia desde la ubicación actual a cada checkpoint
#     distancias_desde_ubicacion_actual = {}
#     for nombre, coordenadas in coordenadas_checkpoints.items():
#         distancia = geodesic(ubicacion_actual, coordenadas).kilometers
#         distancias_desde_ubicacion_actual[nombre] = distancia

#     # Encontrar la ruta más corta desde la ubicación actual hasta C usando Dijkstra
#     ruta_mas_corta_hasta_C = None
#     distancia_ruta_mas_corta_hasta_C = math.inf

#     for checkpoint in checkpoints_no_visitados:
#         distancia = distancias_desde_ubicacion_actual[checkpoint]
#         if distancia < distancia_ruta_mas_corta_hasta_C:
#             ruta_mas_corta_hasta_C = checkpoint
#             distancia_ruta_mas_corta_hasta_C = distancia

#     # Calcular la distancia desde C hasta D
#     checkpoint_C = coordenadas_checkpoints[ruta_mas_corta_hasta_C]
#     checkpoint_D = coordenadas_checkpoints[checkpoints_no_visitados[-1]]
#     distancia_C_a_D = geodesic(checkpoint_C, checkpoint_D).kilometers

#     # Calcular la distancia total desde la ubicación actual hasta D pasando por C
#     distancia_total = distancia_ruta_mas_corta_hasta_C + distancia_C_a_D

#     # Calcular el tiempo total considerando la velocidad promedio
#     tiempo_total = (distancia_total * 60) / velocidad_promedio

#     return distancia_total, format_time_minutes(tiempo_total)

def get_distance_and_time(origin, destination):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "key": GOOGLEMAPS_API_KEY,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK" and len(data["routes"]) > 0:
        distance_in_meters = data["routes"][0]["legs"][0]["distance"]["value"]
        # distance_in_kilometers = distance_in_meters / 1000

        duration_in_seconds = data["routes"][0]["legs"][0]["duration"]["value"]
        duration_formatted = format_time(duration_in_seconds)

        return distance_in_meters, duration_formatted
    else:
        return None, None





def status_text(status):
    if status == "failed":
        return "no completado"
    elif status == "assigned":
        return "asignado"
    elif status == "done":
        return "completado"
    else:
        return status

def format_time_minutes(minutes):
    hours = minutes // 60
    minutes %= 60

    if hours == 0:
        return f"{int(minutes)}m"
    elif minutes == 0:
        return f"{int(hours)}h"
    else:
        return f"{int(hours)}h {(minutes)}m"

def format_time(seconds):
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60
    return f"{hours}h {minutes}m"

def format_time1(days, hours, minutes):
    formatted_time = ""
    if days > 0:
        formatted_time += f"{int(days)}d "
    if hours > 0:
        formatted_time += f"{int(hours)}h "
    formatted_time += f"{int(minutes)}m"
    return formatted_time


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
