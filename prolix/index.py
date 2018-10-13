import json

class IndexEntry:
    """Index Entry contains the attributes allow encoding/decoding a message"""

    DEFAULT_TTL_MINS = 5

    def __init__(self):
        self.storage_key = ""
        self.mapping = []
        self.steno_seq = []
        self.steno_text = ""
        self.ttl_seconds = 60 * IndexEntry.DEFAULT_TTL_MINS

    def to_json_str(self):
        """
        Convert this object to a JSON string

        :return: JSON string containing the data fields in this object
        :rtype: str
        """
        return json.dumps(self.__dict__)

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
