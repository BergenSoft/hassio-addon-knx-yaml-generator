# KNX YAML Generator

This addon is used to create an knx.yaml file which is compatible with the [KNX Integration](https://www.home-assistant.io/integrations/knx/).

# How does it work

This addon is using user defined rules to search for matching group addresses. This rules are defined in a separate generator.yaml file.
In case you want to have some more additional entries that should be added to the result you can add them in an add_entities.yaml file.

# Requirements

-   The most important requirement is that the names of the group addresses follows some defined rules.
-   The exported list of all group addresses from ETS.
-   You need to create a generator.yaml file with all the rules. An example file will be created on the first run.

# Installation

At the moment there are no pre-build docker container available. To install this addon you have to do the following steps:

-   Copy the folder `knx-yaml-generator` into your Home Assistant `/addons` folder
-   Open Home Assistants Addon Store
-   Scan for updates
-   Reload the page
-   Select this local addon and press `Install`

See Home Assistants Addon tutorial for this steps: https://developers.home-assistant.io/docs/add-ons/tutorial/

# Addon configuration

The configuration of the addon is pretty simple. You have just to define some paths to files.

## config: path_generator

The absolute path to the generator.yaml file. If it doesn't exists an example is created.

At the moment the following knx types are supported:

-   light
-   switch
-   binary_sensor
-   sensor
-   cover

The format is the following:

```YAML
light:
  - grp: grp_filter [Optional]
    address: regex
    address_ignore: regex [Optional]
    state_address: regex
    state_address_ignore: regex [Optional]

switch:
  - grp: grp_filter [Optional]
    address: regex
    address_ignore: regex [Optional]
    state_address: regex
    state_address_ignore: regex [Optional]

binary_sensor:
  - grp: grp_filter [Optional]
    state_address: regex
    state_address_ignore: regex [Optional]

sensor:
  - grp: grp_filter [Optional]
    state_address: regex
    state_address_ignore: regex [Optional]
    type: knx_sensor_type

cover:
  - grp: grp_filter [Optional]
    move_long_address: regex
    move_long_address_ignore: regex [Optional]
    move_short_address: regex [Optional]
    move_short_address_ignore: regex [Optional]
    stop_address: regex
    stop_address_ignore: regex [Optional]
    position_address: regex
    position_address_ignore: regex [Optional]
    position_state_address: regex
    position_state_address_ignore: regex [Optional]

```

For each type there can be as much as rules needed.
If you add other key-value entries, they will be ignored.
That means you could also add `comment: Note for me` if you want.

**grp_filter**<br/>
Group address filter are always optional.
You can use them to restrict the group address entries that will be scanned for the rules.

Example:

```YAML
grp: "0/"   #This will match all addresses starting with 0/
grp: "0/1/" #This will match all addresses starting with 0/1/
```

**regex**<br/>
This regex is used to identify the entries that are used and also to identify the name for the generated entity.
If the same name for all required (not optional) fields are found, an entity is generated.
To mark the name that should be used you have to put it in brackets to make a regex group.

For the following example we assume we have the following addresses:

-   **1/0/0** -> Floor1 Room1 Light Table On/Off
-   **1/0/1** -> Floor1 Room1 Light Table Status
-   **1/0/2** -> Floor1 Room1 Light Bed On/Off
-   **1/0/3** -> Floor1 Room1 Light Bed Status

Example:

```YAML
address: "(.*) On/Off"   #This will match
                         #1/0/0 with the name "Floor1 Room1 Light Table" and
                         #1/0/2 with the name "Floor1 Room1 Light Bed"
state_address: "(.*) Status" #This will match
                             #1/0/1 with the name "Floor1 Room1 Light Table" and
                             #1/0/3 with the name "Floor1 Room1 Light Bed"
```

In this example we would get two entities with the names

-   Floor1 Room1 Light Table
-   Floor1 Room1 Light Bed

But only in case all required fields are available

Sometimes it could be hard to create one matching regex.
In this case you can help you by defining a regex ignore rule to limit the found items.
All ignore rules are optional.

Example:

```YAML
move_long_address: "(.*) Up/Down"
move_short_address: "(.*) short Up/Down"
```

The problem here is that the first regex will also find addresses from the second regex.
To prevent that you can define to ignore the items that also would match the short address regex.

```YAML
move_long_address: "(.*) Up/Down"
move_long_address_ignore: "(.*) short Up/Down"
move_short_address: "(.*) short Up/Down"
```

**knx_sensor_type**<br/>
A list with valid values can be found here: https://www.home-assistant.io/integrations/knx/#value-types

## config: path_add_entities

The absolute path to the add_entities.yaml file.
This file is optional and can contain already knx.yaml compatible entries.

```YAML
light:
  - name: "Special"
    address: "4/9/9"
    state_address: "4/9/10"
```

This entries will be merged into the generated knx.yaml file.

## config: path_csv_grp

The absolute path to csv file with the exported values from ETS.

**How to export:**<br/>
In ETS, right click the **Group Addresses** bar and select **Export Group Addresses**.<br/>
Select the following settings:

-   Output Format: CSV
-   CSV Format: 1/1 - Name/Address
-   CSV Separator: Tabulator

## config: path_backup

The absolute path to a directory where the backup of the knx.yaml file is placed.
If the directory doesn't exist, it will be created.

Before overwriting the output file, the existing file is moved to the backup folder and renamed to `original_name_2024_01_01.yaml`.
Only then the new file is generated.

## config: path_output

The absolute path to the output file. A backup will be created before overwriting this file.

To use the generated yaml file, place this in your main `configuration.yaml`

```YAML
knx: !include path/to/generated/knx.yaml
```

# IMPORTANT

To generate a new file, just start the addon.
This will backup the old file and generate the new.
After that the addon is stopped automatically.

After generating the knx.yaml file you have to reload the yaml configuration manually in Home Assistant.

This can be done by openening the `Developer tools` (`Entwicklerwerkzeuge`) and pressing on `KNX` or `ALL YAML-CONFIGURATIONS` button.
