import copy
import json
import standard_logger


class IndexEntry:
    """Index Entry contains the attributes allow encoding/decoding a message"""

    DEFAULT_TTL_MINS = 5

    def __init__(self, logger=None):
        self.logger = logger if logger else standard_logger.get_logger("Index")
        self.object_type = "IndexType"
        self.object_type_version = "V1"
        self.storage_key = ""
        self.steno_seq = []
        self.ttl_seconds = 60 * IndexEntry.DEFAULT_TTL_MINS

    def remove_from_dict(self, dict_to_clean, keys_to_remove):
        """
        Create a shallow copy of supplied dictionary with the specified keys removed

        :param dict_to_clean:
        :param keys_to_remove:
        :return:
        """
        cleaned_dict = copy.copy(dict_to_clean)
        for key in keys_to_remove:
            if key in cleaned_dict:
                del cleaned_dict[key]

        return cleaned_dict

    def to_json_str(self):
        """
        Convert this object to a JSON string

        :return: JSON string containing the data fields in this object
        :rtype: str
        """
        dict_to_serialize = self.remove_from_dict(self.__dict__, ['logger'])
        # print("to_json_str dict_to_serialize {0}".format(dict_to_serialize))
        return json.dumps(dict_to_serialize)

    def __eq__(self, other):
        clean_self = self.remove_from_dict(self.__dict__, ['logger'])
        clean_other = self.remove_from_dict(other.__dict__, ['logger'])
        return clean_self == clean_other

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
    def from_json_str(cls, json_str, logger=None):
        """
        Create an IndexEntry instance from the supplied JSON string

        :param str json_str: JSON string containing IndexEntry data fields
        :param logger: Logger instance
        :return: An initialized IndexEntry instance
        :rtype: IndexEntry
        """
        index_entry = IndexEntry(logger=logger)
        index_entry.__dict__ = json.loads(json_str)
        return index_entry
