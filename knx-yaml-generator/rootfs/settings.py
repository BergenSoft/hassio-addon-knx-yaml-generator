import json
import os
import shutil


class Settings:
    __instance = None

    @staticmethod
    def instance() -> "Settings":
        if Settings.__instance is None:
            Settings.__instance = Settings()

        return Settings.__instance

    def __init__(self) -> None:
        if Settings.__instance is not None:
            raise Exception("Sorry, call Settings.instance()")

        # singleton
        Settings.__instance = self

        # Read user settings
        if os.path.isfile("/data/options.json"):
            with open("/data/options.json") as json_data:
                settings = json.load(json_data)
        elif os.path.isfile("./data/options.json"):
            with open("./data/options.json") as json_data:
                settings = json.load(json_data)

        # publish path properties
        self.path_generator = settings["path_generator"]
        self.path_add_entities = settings["path_add_entities"]
        self.path_csv_grp = settings["path_csv_grp"]
        self.path_backup = settings["path_backup"]
        self.path_output = settings["path_output"]

        # Copy examples if needed
        self.__prepareExample("./examples/generator.yaml", self.path_generator)
        self.__prepareExample("./examples/add_entities.yaml", self.path_add_entities)
        self.__prepareExample("./examples/grp.csv", self.path_csv_grp)

        # create backup folder
        if not os.path.isdir(self.path_backup):
            os.mkdir(self.path_backup)

    def __prepareExample(self, examplePath: str, targetPath: str) -> None:
        if not os.path.isfile(targetPath):
            shutil.copy(examplePath, targetPath)
