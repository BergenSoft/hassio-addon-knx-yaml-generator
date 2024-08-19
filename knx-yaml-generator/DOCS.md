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

All knx entity types that currently exists are supported:

-   binary_sensor
-   button
-   climate
-   cover
-   date
-   datetime
-   fan
-   light
-   notify
-   number
-   scene
-   select
-   sensor
-   switch
-   text
-   time
-   weather

The format is the following:

```YAML
<knx entity name>:
  - grp: <grp_filter> [Optional]
    name: <name_pattern> [Optional]
    address_name: <regex>  [Required or Optional, see hassio knx documentation]
    address_name_ignore: <regex> [Optional]

```

Each address that exists for a specific knx type can be used.
You can always append "_ignore" to reduce the addresses that where found, if needed.

Here an example for a light
```YAML
light:
  - grp: 1/
    name: ${middle} ${name}
    address: "(.*) On/Off"
    address_ignore: ".* Secret On/Off"
    state_address: "(.*) Status"

```

For each type there can be as much rules as needed.

**grp_filter**<br/>
Group address filter are always optional.
You can use them to restrict the group address entries that will be scanned for the rules.

Example:

```YAML
grp: "0/"   #This will match all addresses starting with 0/
grp: "0/1/" #This will match all addresses starting with 0/1/
```

**name_pattern**<br/>
Name pattern are always optional.
With the name pattern you can define the resulting name that will be used in the knx entities.
The default is to use the part of the group address name that is found by the regex (see next point).
You can define some static text or use some placeholders.

You can use this placeholders:

-   `${main}` The name of the main group
-   `${middle}` The name of the middle group
-   `${name}` The name of the regex matching name of the last group

Example:

```YAML
# Lets assume you have this structure:
# 1     Type
# 1/0   Floor 0
# 1/0/0 Room 1 On/Off
# 1/0/1 Room 1 Status
#
# and the regex will match "Room 1"

name: ${name}                   # => Room 1  (This is the default)
name: ${middle} ${name}         # => Floor 0 Room 1
name: ${main} ${middle} ${name} # => Type Floor 0 Room 1
name: ${main} ${name}           # => Type Room 1
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

Before overwriting the output file, the existing file is moved to the backup folder and renamed to `original_name_yyyy-mm-ss_hhmmss.yaml`.
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
