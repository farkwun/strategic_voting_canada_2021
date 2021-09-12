from sv.svdb import SVDatabase
import sv.svlib
import json

new_db = SVDatabase("db/sv_tables.db")

new_db.drop_table("districts")

new_db.create_districts_table()

f = open("district_codes.txt", "r")

district_codes = [line.strip() for line in f]

f.close()

for code in district_codes:
    print(code)
    district = sv.svlib.get_district_info_by_id(str(code))
    new_db.add_district(
        district.district_id, json.dumps(district.properties), district.last_updated
    )
