import json

from sv.db import Database
from datetime import date
from sv.district import District


class SVDatabase(Database):
    def district_exists(self, district_id):
        sql = "SELECT id FROM districts where id = '{district_id}'".format(
            district_id=district_id
        )
        self.query(sql)
        return len(self.fetchall()) != 0

    def get_district_from_id(self, district_id):
        sql = "SELECT * FROM districts WHERE id = '{district_id}'".format(
            district_id=district_id
        )
        self.query(sql)
        return District(self.fetchone())

    def add_district(self, district_id, district_properties, last_updated):
        sql = "INSERT INTO districts VALUES('{id}', '{properties}', '{last_updated}')".format(
            id=district_id,
            properties=json.dumps(district_properties),
            last_updated=last_updated,
        )
        self.write(sql)

    def create_districts_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS districts (
            id varchar(250) PRIMARY KEY ,
            properties JSON NOT NULL,
            last_updated TEXT NOT NULL
        )
        """
        self.write(sql)
