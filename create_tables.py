from sv.svdb import SVDatabase

new_db = SVDatabase('db/sv_tables.db')

new_db.drop_table('districts')

new_db.create_districts_table()

new_db.add_district('test_district', {"fake_properties:": 1234})
