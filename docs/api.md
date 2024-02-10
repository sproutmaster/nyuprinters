# API [/api]

The system offers a RESTful API to interact with almost all aspects of services.

## Locations [/locations]

### /GET : Get location -> [ { } ] | { }

Query parameters:
- `location_id` (int, optional): The id of the location
- `short` (string, optional): The short name of the location
- Nothing: Returns info of all locations

### /PUT : Add a new location ->  { }

Request body:
- `short` (string, required): The short name of the location
- `name` (string, required): The name of the location
- `description` (string, optional): Description of the location
- `visible` (string, optional): `true`|`false` to mark the location visible to the public

### /PATCH : Update a location ->  { }

Request body:
- `location_id` (int, required): The id of the location
- `short` (string, required): The short name of the location
- `name` (string, required): The name of the location
- `description` (string, optional): Description of the location
- `visible` (string, optional): `true`|`false` to mark the location visible to the public

### /DELETE : Delete a location ->  { }

Request body:
- `location_id` (int, required): The id of the location

## Printers [/printers]

### /GET : Get printers -> [ { } ] | { }

Query parameters:
- `printer_id` (int, optional): The id of the printer
- `location` (string, optional): The short name of the location
- Nothing: Returns info of all printers

### /POST : Get status of a printer directly from sourced ->  { }

Request body:
- `ip` (string, required): The IPv4 address of the printer

### /PUT : Add a new printer ->  { }

Request body:
- `name` (string, required): The name of the printer
- `brand` (string, required): The brand of the printer (`hp`|`lanier`)
- `type` (string, required): The type of the printer (`true` for color, `false` for grayscale)
- `model` (string, optional): The model of the printer
- `ip` (string, required): The IPv4 address of the printer
- `location` (string, required): The short name of the location
- `comment` (string, optional): A comment about the printer
- `visible` (string, optional): `true`|`false` to mark the printer visible to the public

### /PATCH : Update a printer ->  { }

Request body:
- `printer_id` (int, required): The id of the printer
- `name` (string, required): The name of the printer
- `brand` (string, required): The brand of the printer (`hp`|`lanier`)
- `type` (string, required): The type of the printer (`true` for color, `false` for grayscale)
- `model` (string, optional): The model of the printer
- `ip` (string, required): The IPv4 address of the printer
- `location` (string, required): The short name of the location
- `comment` (string, optional): A comment about the printer
- `visible` (string, optional): `true`|`false` to mark the printer visible to the public

### /DELETE : Delete a printer ->  { }

Request body:
- `printer_id` (int, required): The id of the printer

## Settings [/settings]

### /GET : Get settings -> [ { } ] | { }

Query parameters:
- `key` (string, optional): The key of the setting
- Nothing: Returns all settings

### /PATCH : Update a setting ->  { }

Request body:
- `key` (string, required): The id of the setting
- `value` (string, required): The value of the setting

### /POST :Reset settings to default ->  { }

Request body:
- `reset` (string, required): `true` to reset settings to default

## Users [/users]

### /GET : Get users -> [ { } ] | { }

Query parameters:

- `user_id` (int, optional): The id of the user
- Nothing: Returns info of all users

### /PUT : Add a new user ->  { }

Request body:
- `netid` (string, required): The username of the user
- `name` (string, required): The name of the user
- `type` (string, required): The type of the user (`superuser`|`user`)
- `password` (string, required): Initial password for the user

### /PATCH : Update a user ->  { }

Request body:
- `user_id` (int, required): The id of the user
- `netid` (string, required): The username of the user
- `name` (string, required): The name of the user
- `type` (string, required): The type of the user (`superuser`|`user`)
- `password` (string, optional): New password for the user

### /DELETE : Delete a user ->  { }

Request body:
- `user_id` (int, required): The id of the user
