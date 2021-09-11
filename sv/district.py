class District:
    def __init__(self, row_tuple):
        (self.district_id, self.properties, self.last_updated) = row_tuple

    def __repr__(self):
        return ("<District object - id: {user_id}, "
                "last_updated: {last_updated}, "
                "last_updated: {last_updated}, "
                "options: {options}>").format(
                    district_id=self.district_id,
                    properties=self.properties,
                    last_updated=self.last_updated
                )
