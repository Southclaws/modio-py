import logging
import io
import struct

from .exceptions import (InvalidModioFormat, IncorrectModioVersion,
                         ModioTagOverflow)
from .tag import ModioFileTag
from .utils import _tag_IntToString


MODIO_VERSION = 20


class ModioSession:

    # Attributes for a modio object:

    # self.filename
    # self.filemode
    # self.filever
    # self.filelen
    # self.numtags

    # self.filedata
    # self.tagdict

    def __init__(self, filename, filemode):
        logging.info("%s, %s, %s" % (self, filename, filemode))

        self.filename = filename
        self.filemode = filemode

    def __enter__(self):
        logging.info("%s" % (self))

        self.filedata = []

        self.filever = 0
        self.filelen = 0
        self.numtags = 0
        self.tagdict = {}

        if self.filemode == "r":
            return self.__read__()

        elif self.filemode == "w":
            return self.__write__()

        return

    def __exit__(self, *err):
        logging.info("%s, %s" % (self, err))
        self.close()

    def __read__(self):
        logging.info("%s" % (self))

        filehandle = io.open(self.filename, "rb")

        filedata = filehandle.read()
        fmat = "<%dI" % (len(filedata) // 4)
        self.filedata = list(struct.unpack(fmat, filedata))

        filehandle.close()

        if len(self.filedata) < 3:
            raise InvalidModioFormat

        self.filever = self.filedata[0]

        if self.filever != MODIO_VERSION:
            raise IncorrectModioVersion

        self.filelen = self.filedata[1]

        # No file size limit

        self.numtags = self.filedata[2]

        if self.numtags > 4096:
            raise ModioTagOverflow

        head_pointer = 3

        for i in range(self.numtags):

            tagname = self.filedata[head_pointer]
            physpos = self.filedata[head_pointer + 1]
            tagsize = self.filedata[3 + (self.numtags * 2) + physpos + 1]
            tagdata = self.filedata[3 + (self.numtags * 2) + physpos + 2: (
                3 + (self.numtags * 2) + physpos + 2 + tagsize)]

            self.tagdict[_tag_IntToString(tagname)] = ModioFileTag(
                tagname, tagdata)

            head_pointer += 2

        return self

    def __write__(self):
        logging.info("%s" % (self))

        return self

    def close(self):
        logging.info("%s" % (self))

        # Upon closing the file, if it was in write mode then write the data.
        if self.filemode == "w":
            with io.open(self.filename, "wb") as f:
                data = self.get_bytes()
                f.write(struct.pack('%dI' % (len(data)), *data))

        return

    def get_bytes(self):
        logging.info("%s" % (self))

        # 3 cells for the metadata, then tag count x 2 (tag name + tag physpos)
        header_size = 3 + (len(self.tagdict) * 2)
        body_size = 0

        # version, file length and tag count (file length is added afterwards)
        header = [MODIO_VERSION, 0, len(self.tagdict)]
        body = []

        # Points at the physical position of the current tag data block
        header_physpos_pointer = 0

        # Stores the size of the current tag data block (including metadata)
        tag_size = 0

        for tag in self.tagdict.values():
            logging.info("APPENDING TAG %d %s %s" % (
                tag.get_name(), tag.get_name_str(), tag.get_data()))
            # body size = sum of tag total sizes (tag + n + n data cells)
            tag_size = tag.get_total_size()
            body_size += tag_size

            logging.info("TAG SIZE: %d" % (tag_size))

            # Append two cells to header (the tag name and the physical pos)
            header += [tag.get_name(), header_physpos_pointer]

            # Increment the header physical position pointer by the data size
            header_physpos_pointer += tag_size

            # Append the actual data block to the body (including metadata)
            body.extend(tag.get_data_block())

        header[1] = header_size + body_size

        logging.info("HEADER SIZE: %d BODY SIZE: %d TOTAL: %d" %
                     (header_size, body_size, header_size + body_size))

        return header + body

    def get(self, tag=""):
        logging.info("%s, %s" % (self, tag))

        if tag:
            return self.tagdict[tag]

        else:
            return list(self.tagdict.values())

    def put(self, tag, data):
        logging.info("%s, %s" % (self, tag))

        self.tagdict[tag] = ModioFileTag(tag, data)

        return

    def metadata(self):
        return self.filever, self.filelen, self.numtags

    def version(self):
        return self.filever

    def file_size(self):
        return self.filelen

    def num_tags(self):
        return self.numtags
