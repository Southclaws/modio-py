import io
import struct
import string
import logging


version = 20
mode_read = 0
mode_write = 1


class ModioFileTag:

	def __init__(self, tag, data):
		validate_data_block_types(data)

		if type(tag) is str:
			self.tag = _tag_StringToInt(tag)
			self.data = data

		else:
			self.tag = tag
			self.data = data

	def get_name(self):
		return self.tag

	def get_data(self):
		return self.data

	def get_size(self):
		return len(self.data)

	def get_total_size(self):
		return len(self.data) + 2

	def get_name_str(self):
		return _tag_IntToString(self.tag)

	def get_data_block(self):
		result = [self.tag, len(self.data)]
		result.extend(self.data)
		return result

	def get_data_format(self):
		data = []
		tmp = ""
		for i in self.data:
			if 32 <= i < 127:
				tmp = tmp + "".join(chr(i))

			else:
				if tmp:
					data.append(tmp)
					del(tmp)

				data.append(i)

		return data


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
		logging.debug("__init__: %s"%(self))

		self.filename = filename
		self.filemode = filemode

	def __enter__(self):
		logging.debug("__enter__: %s"%(self))

		self.filedata = []

		self.filever = 0
		self.filelen = 0
		self.numtags = 0
		self.tagdict = {}

		if self.filemode == mode_read:
			return self.__read__()

		elif self.filemode == mode_write:
			return self.__write__()

		return

	def __exit__(self, *err):
		logging.debug("__exit__: %s, %s"%(self, err))
		self.close()

	def __read__(self):
		logging.debug("__read__")

		try:
			filehandle = io.open(self.filename, "rb")

		except FileNotFoundError:
			return 0

		filedata = filehandle.read()
		fmat = "<%dI" % (len(filedata) // 4)
		self.filedata = list(struct.unpack(fmat, filedata))

		filehandle.close()

		self.filever = self.filedata[0]
		self.filelen = self.filedata[1]
		self.numtags = self.filedata[2]

		head_pointer = 3

		for i in range(self.numtags):

			tagname = self.filedata[head_pointer]
			physpos = self.filedata[head_pointer + 1]
			tagsize = self.filedata[3 + (self.numtags * 2) + physpos + 1]
			tagdata = self.filedata[3 + (self.numtags * 2) + physpos + 2 : (3 + (self.numtags * 2) + physpos + 2 + tagsize)]

			self.tagdict[_tag_IntToString(tagname)] = ModioFileTag(tagname, tagdata)

			head_pointer += 2

		return self

	def __write__(self):
		logging.debug("__write__")

		return self

	def close(self):
		logging.debug("close: %s"%(self))

		if self.filemode == mode_write:

			with io.open(self.filename, "wb") as f:
				data = self.get_bytes()

				for i, j in enumerate(data):
					#print("[%02d/%02d] : %d"%(i, len(data), data[i]))
					print(i, type(data[i]), data[i])

				print(struct.pack('%dI'%(len(data)), *data))

				f.write(struct.pack('%dI'%(len(data)), *data))

		return

	def get_bytes(self):
		# 3 cells for the metadata, then tag count x 2 (tag name + tag physpos)
		header_size = 3 + (len(self.tagdict) * 2)
		body_size = 0

		# version, file length and tag count (file length is added afterwards)
		header = [version, 0, len(self.tagdict)]
		body = []

		# Points at the physical position of the current tag data block
		header_physpos_pointer = 0

		# Stores the size of the current tag data block (including metadata)
		tag_size = 0

		for tag in self.tagdict.values():
			print("APPENDING TAG", tag.get_name(), tag.get_name_str(), tag.get_data())
			# body size = sum of tag total sizes (tag + n + n data cells)
			tag_size = tag.get_total_size()
			body_size += tag_size

			print("TAG SIZE: ", tag_size)

			# Append two cells to the header (the tag name and the physical pos)
			header += [tag.get_name(), header_physpos_pointer]

			# Increment the header physical position pointer by the data size
			header_physpos_pointer += tag_size

			# Append the actual data block to the body (including metadata)
			body.extend(tag.get_data_block())

		header[1] = header_size + body_size

		print("HEADER SIZE: %d BODY SIZE: %d TOTAL: %d"%(header_size, body_size, header_size+body_size))

		return header + body

	def get(self, tag = ""):
		logging.debug("get: %s, %s"%(self, tag))

		if tag:
			return self.tagdict[tag]

		else:
			return list(self.tagdict.values())

	def put(self, tag, data):
		logging.debug("put: %s, %s"%(self, tag))

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



def open(filename, filemode):
	m = ModioSession(filename, filemode)
	return m


#
#	Utility functions
#


def _tag_StringToInt(s):
	if len(s) != 4:
		return 0

	return ((ord(s[0])<<24)|(ord(s[1])<<16)|(ord(s[2])<<8)|(ord(s[3])))

def _tag_IntToString(i):
	s = []

	s.append(str(chr((i>>24) & 0xFF)))
	s.append(str(chr((i>>16) & 0xFF)))
	s.append(str(chr((i>>8) & 0xFF)))
	s.append(str(chr(i & 0xFF)))

	return "".join(s)

# Ensures all elements in 'data' are uints
def validate_data_block_types(data):
	for i, d in enumerate(data):
		datatype = type(d)

		# If the data type is a string, insert each char as a uint
		if datatype == str:
			# Delete the existing element (the string)
			del(data[i])

			# Run through the string, grab each character integer and insert it
			pos = 0
			for char in d:
				data.insert(i + pos, ord(char))
				pos += 1

		elif datatype != int:
			return 0

	return 1