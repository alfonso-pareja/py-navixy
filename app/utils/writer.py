import json

class JsonWriter:
    @staticmethod
    def write_json(file_path, data):
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
        except Exception as e:
            raise Exception(f"Error al escribir JSON en {file_path}: {e}")
