import os
import time
import yaml
from pathlib import Path

from settings import Settings
from csvReader import CsvReader


class MyDumper(yaml.SafeDumper):
    # HACK: insert blank lines between top-level objects
    # source: https://github.com/yaml/pyyaml/issues/127
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


class Generator:
    __instance = None
    __result = {}
    __config = {
        "binary_sensor": {
            "required_fields": [
                "state_address"
            ],
            "optional_fields": [
            ]
        },
        "button": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
            ]
        },
        "climate": {
            "required_fields": [
                "temperature_address",
                "target_temperature_state_address"
            ],
            "optional_fields": [
                "target_temperature_address",
                "setpoint_shift_address",
                "setpoint_shift_state_address",
                "active_state_address",
                "command_value_state_address",
                "operation_mode_address",
                "operation_mode_state_address",
                "controller_status_address",
                "controller_status_state_address",
                "controller_mode_address",
                "controller_mode_state_address",
                "heat_cool_address",
                "heat_cool_state_address",
                "operation_mode_frost_protection_address",
                "operation_mode_night_address",
                "operation_mode_comfort_address",
                "operation_mode_standby_address",
                "on_off_address",
                "on_off_state_address"
            ]
        },
        "cover": {
            "required_fields": [
            ],
            "optional_fields": [
                "move_long_address",
                "move_short_address",
                "stop_address",
                "position_address",
                "position_state_address",
                "angle_address",
                "angle_state_address"
            ],
            "require_one_of": ["move_long_address", "position_address"]
        },
        "date": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address"
            ]
        },
        "datetime": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address"
            ]
        },
        "fan": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address",
                "oscillation_address",
                "oscillation_state_address"
            ]
        },
        "light": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address",
                "brightness_address",
                "brightness_state_address",
                "color_address",
                "rgbw_address",
                "rgbw_state_address",
                "hue_address",
                "hue_state_address",
                "saturation_address",
                "saturation_state_address",
                "xyy_address",
                "xyy_state_address",
                "color_temperature_address",
                "color_temperature_state_address"
            ]
        },
        "notify": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
            ]
        },
        "number": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address"
            ]
        },
        "scene": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
            ]
        },
        "select": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address"
            ]
        },
        "sensor": {
            "required_fields": [
                "state_address"
            ],
            "optional_fields": [
            ]
        },
        "switch": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address"
            ]
        },
        "text": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address"
            ]
        },
        "time": {
            "required_fields": [
                "address"
            ],
            "optional_fields": [
                "state_address"
            ]
        },
        "weather": {
            "required_fields": [
                "address_temperature",
            ],
            "optional_fields": [
                "address_brightness_south",
                "address_brightness_west",
                "address_brightness_east",
                "address_brightness_north",
                "address_wind_speed",
                "address_rain_alarm",
                "address_frost_alarm",
                "address_wind_alarm",
                "address_day_night",
                "address_air_pressure",
                "address_humidity",
                "sync_state",
            ]
        }
    }

    def instance() -> "Generator":
        if Generator.__instance is None:
            Generator.__instance = Generator()

        return Generator.__instance

    def __init__(self) -> None:
        if Generator.__instance is not None:
            raise Exception("Sorry, call Generator.instance()")

        # singleton
        Generator.__instance = self

    def run(self) -> None:
        # read generator file
        with open(Settings.instance().path_generator, "r") as file:
            generator = yaml.safe_load(file)

        # handle entries
        for key in generator:
            if key not in self.__config:
                print("Found invalid key in generator file: " + key)
                continue

            for rule in generator[key]:
                self.__handleRule(key, self.__config[key], rule)

        # read add_entries and add it to the result
        addEntitiesPath = Settings.instance().path_add_entities
        if addEntitiesPath is not None and addEntitiesPath != "" and os.path.isfile(addEntitiesPath):
            with open(addEntitiesPath, "r") as file:
                addEntries = yaml.safe_load(file)

            if addEntries is not None:
                for key in addEntries:
                    if key not in self.__result:
                        self.__result[key] = []
                    self.__result[key] += addEntries[key]

    def saveResult(self) -> None:
        targetPath = Settings.instance().path_output

        # Make backup if target file exists
        if os.path.isfile(targetPath):
            backupPath = os.path.join(Settings.instance().path_backup, Path(targetPath).stem + "_" + time.strftime("%Y-%m-%d_%H%M%S") + Path(targetPath).suffix)
            os.rename(targetPath, backupPath)

        # write target file
        with open(targetPath, "w") as file:
            file.writelines([
                "# DO NOT EDIT THIS FILE\n",
                "#\n",
                "# This file is generated by the Home Assistant Addon \"KNX YAML Generator\"\n",
                "# It will be overwritten when running the addon.\n",
                "# Don't forget to reload the yaml configurations in Home Assistant after recreating.\n",
                "#\n",
                "# DO NOT EDIT THIS FILE\n\n",
            ])
            yaml.dump(self.__result, file, Dumper=MyDumper, allow_unicode=True, sort_keys=False)

    def __handleRule(self, key: str, config, rule) -> None:
        param = []

        for conf in config["required_fields"]:
            items = CsvReader.instance().query(rule.get("grp", None), rule.get(conf, None), rule.get(conf + "_ignore", None), rule.get("name", None))
            param.append({
                "data": items,
                "required": True,
                "name": conf
            })

        for conf in config["optional_fields"]:
            items = CsvReader.instance().query(rule.get("grp", None), rule.get(conf, None), rule.get(conf + "_ignore", None), rule.get("name", None))
            param.append({
                "data": items,
                "required": False,
                "name": conf
            })

        # Add static values
        for ruleKey, ruleValue in rule.items():
            # Ignore all handled rules
            match ruleKey:
                case "grp" | "name":
                    continue

            if ruleKey in config["required_fields"] or ruleKey.replace("_ignore", "") in config["required_fields"]:
                continue

            if ruleKey in config["optional_fields"] or ruleKey.replace("_ignore", "") in config["optional_fields"]:
                continue

            param.append({
                "custom_data": ruleValue,
                "name": ruleKey
            })

        self.__addToResult(param, config.get("require_one_of", None), key)

    def __addToResult(self, datas, requireOneOf, key) -> None:
        tempResult = {}

        for dataItem in datas:
            if "data" in dataItem:
                for item in dataItem["data"]:
                    if item.matchName not in tempResult:
                        tempResult[item.matchName] = {
                            "name": item.matchName
                        }

                    tempResult[item.matchName][dataItem["name"]] = item.address

        # Add constant values to items
        for dataItem in datas:
            if "custom_data" in dataItem:
                for matchName in tempResult:
                    if isinstance(dataItem["custom_data"], list):
                        tempResult[matchName][dataItem["name"]] = dataItem["custom_data"][:]
                    else:
                        tempResult[matchName][dataItem["name"]] = dataItem["custom_data"]

        # Put all complete items to result
        result = []

        for matchName in tempResult:
            complete = True
            for dataItem in datas:
                if "data" in dataItem:
                    if dataItem["required"] and dataItem["name"] not in tempResult[matchName]:
                        complete = False
                        break

            if complete:
                # Check if require_one_of is fullfilled
                if requireOneOf is not None:
                    foundOne = False
                    for required in requireOneOf:
                        if required in tempResult[matchName]:
                            foundOne = True
                            break

                if requireOneOf is None or foundOne:
                    result.append(tempResult[matchName])

        if len(result) > 0:
            if key not in self.__result:
                self.__result[key] = []

            self.__result[key] += result
