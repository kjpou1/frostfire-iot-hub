import json


class TVAppMapper:
    def __init__(self):
        """
        Initialize dictionaries to hold the app mappings.
        """
        self.tv_apps = {}  # Maps TV app names to their URIs
        self.alexa_to_tv_mapping = {}  # Maps Alexa app identifiers to TV app URIs
        self.alexa_name_to_identifier = {}  # Maps Alexa app names to their identifiers

    def set_tv_apps(self, apps_list):
        """
        Set the TV applications dictionary.

        :param apps_list: List of dictionaries containing app information (title, uri, icon).
        """
        # Convert all titles to lowercase for case-insensitive matching
        self.tv_apps = {app["title"].lower(): app["uri"] for app in apps_list}
        # Rebuild the mapping from Alexa app identifier to TV app identifier
        self.build_alexa_to_tv_mapping()

    def load_alexa_apps(self, file_path):
        """
        Load the Alexa applications from a JSON file.

        :param file_path: Path to the JSON file containing Alexa app data.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Create mappings from Alexa data with case-insensitive keys
                self.alexa_to_tv_mapping = {
                    app["identifier"]: app["name"].lower()
                    for app in data.get("apps", [])
                }
                self.alexa_name_to_identifier = {
                    app["name"].lower(): app["identifier"]
                    for app in data.get("apps", [])
                }
        except Exception as e:
            print(f"Error loading Alexa apps from {file_path}: {e}")

    def build_alexa_to_tv_mapping(self):
        """
        Build the mapping from Alexa identifiers to TV app URIs.
        """
        # Rebuild the mapping for case-insensitivity
        for alexa_identifier, app_name in self.alexa_to_tv_mapping.items():
            if app_name in self.tv_apps:
                self.alexa_to_tv_mapping[alexa_identifier] = self.tv_apps[app_name]

    def get_tv_app_uri_by_name_or_identifier(self, identifier_or_name):
        """
        Get the TV app URI by either Alexa identifier or Alexa app name.

        :param identifier_or_name: The app identifier or app name used by Alexa.
        :return: The TV app URI or None if not found.
        """
        # Try to get the app URI by identifier
        app_uri = self.get_tv_app_identifier(identifier_or_name)
        if app_uri:
            return app_uri

        # If identifier_or_name is actually an app name, get the identifier first
        alexa_identifier = self.get_alexa_identifier(identifier_or_name)
        if alexa_identifier:
            return self.get_tv_app_identifier(alexa_identifier)

        return None

    def get_tv_app_identifier(self, alexa_identifier):
        """
        Get the TV app identifier corresponding to an Alexa app identifier.

        :param alexa_identifier: The app identifier used by Alexa.
        :return: The app identifier string for the TV, or None if not found.
        """
        return self.alexa_to_tv_mapping.get(alexa_identifier)

    def get_alexa_identifier(self, alexa_app_name):
        """
        Get the Alexa identifier corresponding to an Alexa app name.

        :param alexa_app_name: The app name used by Alexa.
        :return: The app identifier string for Alexa, or None if not found.
        """
        return self.alexa_name_to_identifier.get(alexa_app_name.lower())
