import json


class JsonUtils:
    @staticmethod
    def load_json_file(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {e}")
            return None
