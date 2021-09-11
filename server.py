from bottle import route, run, request, response, default_app
import json
import sv.svdb
import requests
import time
import sv.settings
import sqlite3
from threading import Thread

db_file = sv.settings.DB_LOCATION

DATABASE = sv.svdb.SVDatabase(db_file)


@route("/district/<district_id>")
def district_info(district_id):
    if DATABASE.district_exists(district_id):
        district = DATABASE.get_district_from_id(district_id)
        return {
            "id": district_id,
            "properties": district.properties,
            "last_updated": district.last_updated,
        }
    else:
        return {"error": "No such district {}".format(district_id)}


run(host="0.0.0.0", port=8080, debug=True, reloader=True)
