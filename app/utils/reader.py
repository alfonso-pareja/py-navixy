import json

class JsonReader:
    @staticmethod
    def get_json(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo {file_path} no fue encontrado.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error al decodificar JSON en {file_path}: {e}")
