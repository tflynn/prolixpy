import json

class IndexEntry:
    """Index Entry contains the attributes allow encoding/decoding a message"""

    DEFAULT_TTL_MINS = 5

    def __init__(self):
        self.object_type = "IndexType"
        self.object_type_version = "V1"
        self.storage_key = ""
        self.mapping = []
        self.steno_seq = []
        self.ttl_seconds = 60 * IndexEntry.DEFAULT_TTL_MINS

    def to_json_str(self):
        """
        Convert this object to a JSON string

        :return: JSON string containing the data fields in this object
        :rtype: str
        """
        return json.dumps(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        sep = " "
        return ("ot: {0}".format(self.object_type)
                + sep + "otv: {0}".format(self.object_type_version)
                + sep + "sk: {0}".format(self.storage_key)
                + sep + "m: {0}".format('...')
                + sep + "ss: {0}".format('...')
                + sep + "ttl: {0}".format(self.ttl_seconds)
                )

    def __repr__(self):
        self.__str__()

    @classmethod
    def from_json_str(cls, json_str):
        """
        Create an IndexEntry instance from the supplied JSON string

        :param str json_str: JSON string containing IndexEntry data fields
        :return: An initialized IndexEntry instance
        :rtype: IndexEntry
        """
        index_entry = IndexEntry()
        index_entry.__dict__ = json.loads(json_str)
        return index_entry
