import logging

from .utils import (_tag_IntToString, _tag_StringToInt,
                    validate_data_block_types)


class ModioFileTag:

    def __init__(self, tag, data):
        logging.info("[__init__] : %s, %s, %s" % (self, tag, data))

        data = validate_data_block_types(data)

        if type(tag) is str:
            self.tag = _tag_StringToInt(tag)
            self.data = data

        else:
            self.tag = tag
            self.data = data

    def get_name(self):
        logging.info("[get_name] : %s" % (self))

        return self.tag

    def get_data(self):
        logging.info("[get_data] : %s" % (self))

        return self.data if len(self.data) > 1 else self.data[0]

    def get_size(self):
        logging.info("[get_size] : %s" % (self))

        return len(self.data)

    def get_total_size(self):
        logging.info("[get_total_size] : %s" % (self))

        return len(self.data) + 2

    def get_name_str(self):
        logging.info("[get_name_str] : %s" % (self))

        return _tag_IntToString(self.tag)

    def get_data_block(self):
        logging.info("[get_data_block] : %s" % (self))

        result = [self.tag, len(self.data)]
        result.extend(self.data)
        return result

    def get_data_format(self):
        logging.info("[get_data_format] : %s" % (self))

        data = []
        for i in self.data:
            data.append(i)

        return data
