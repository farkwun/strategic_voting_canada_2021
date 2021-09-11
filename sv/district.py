import json


class District:
    def __init__(self, row_tuple):
        (self.district_id, self.properties, self.last_updated) = row_tuple
        if isinstance(self.properties, str):
            self.properties = json.loads(self.properties)

    def __repr__(self):
        return (
            "<District object - id: {district_id}, "
            "properties: {properties}, "
            "last_updated: {last_updated}>"
        ).format(
            district_id=self.district_id,
            properties=self.properties,
            last_updated=self.last_updated,
        )
