import io
import struct
import string


# "constant"
def MODIO_VERSION():
	return 20

MODIO_DEBUG = False


class ModioFileTag:

	def __init__(self, tag, data):
		dp("[__init__] : %s, %s, %s"%(self, tag, data))

		data = validate_data_block_types(data)

		if type(tag) is str:
			self.tag = _tag_StringToInt(tag)
			self.data = data

		else:
			self.tag = tag
			self.data = data

	def get_name(self):
		dp("[get_name] : %s"%(self))

		return self.tag

	def get_data(self):
		dp("[get_data] : %s"%(self))

		return self.data if len(self.data) > 1 else self.data[0]

	def get_size(self):
		dp("[get_size] : %s"%(self))

		return len(self.data)

	def get_total_size(self):
		dp("[get_total_size] : %s"%(self))

		return len(self.data) + 2

	def get_name_str(self):
		dp("[get_name_str] : %s"%(self))

		return _tag_IntToString(self.tag)

	def get_data_block(self):
		dp("[get_data_block] : %s"%(self))

		result = [self.tag, len(self.data)]
		result.extend(self.data)
		return result

	def get_data_format(self):
		dp("[get_data_format] : %s"%(self))

		data = []
		tmp = ""
		for i in self.data:
#			if 32 <= i < 127:
#				tmp = tmp + "".join(chr(i))
#
#			else:
#				if tmp:
#					data.append(tmp)
#					del(tmp)
#
#				data.append(i)
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
		dp("[__init__] : %s, %s, %s"%(self, filename, filemode))

		self.filename = filename
		self.filemode = filemode

	def __enter__(self):
		dp("[__enter__] : %s"%(self))

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
		dp("[__exit__] : %s, %s"%(self, err))
		self.close()

	def __read__(self):
		dp("[__read__] : %s"%(self))

		filehandle = io.open(self.filename, "rb")

		filedata = filehandle.read()
		fmat = "<%dI" % (len(filedata) // 4)
		self.filedata = list(struct.unpack(fmat, filedata))

		filehandle.close()

		if len(self.filedata) < 3:
			raise InvalidModioFormat

		self.filever = self.filedata[0]

		if self.filever != MODIO_VERSION():
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
			tagdata = self.filedata[3 + (self.numtags * 2) + physpos + 2 : (3 + (self.numtags * 2) + physpos + 2 + tagsize)]

			self.tagdict[_tag_IntToString(tagname)] = ModioFileTag(tagname, tagdata)

			head_pointer += 2

		return self

	def __write__(self):
		dp("[__write__] : %s"%(self))

		return self

	def close(self):
		dp("[close] : %s"%(self))

		# Upon closing the file, if it was in write mode then write the data.
		if self.filemode == "w":
			with io.open(self.filename, "wb") as f:
				data = self.get_bytes()
				f.write(struct.pack('%dI'%(len(data)), *data))

		return

	def get_bytes(self):
		dp("[get_bytes] : %s"%(self))

		# 3 cells for the metadata, then tag count x 2 (tag name + tag physpos)
		header_size = 3 + (len(self.tagdict) * 2)
		body_size = 0

		# version, file length and tag count (file length is added afterwards)
		header = [MODIO_VERSION(), 0, len(self.tagdict)]
		body = []

		# Points at the physical position of the current tag data block
		header_physpos_pointer = 0

		# Stores the size of the current tag data block (including metadata)
		tag_size = 0

		for tag in self.tagdict.values():
			dp("[get_bytes] : APPENDING TAG %d %s %s"%(tag.get_name(), tag.get_name_str(), tag.get_data()))
			# body size = sum of tag total sizes (tag + n + n data cells)
			tag_size = tag.get_total_size()
			body_size += tag_size

			dp("[get_bytes] : TAG SIZE: %d"%(tag_size))

			# Append two cells to the header (the tag name and the physical pos)
			header += [tag.get_name(), header_physpos_pointer]

			# Increment the header physical position pointer by the data size
			header_physpos_pointer += tag_size

			# Append the actual data block to the body (including metadata)
			body.extend(tag.get_data_block())

		header[1] = header_size + body_size

		dp("[get_bytes] : HEADER SIZE: %d BODY SIZE: %d TOTAL: %d"%(header_size, body_size, header_size+body_size))

		return header + body

	def get(self, tag = ""):
		dp("[get] : %s, %s"%(self, tag))

		if tag:
			return self.tagdict[tag]

		else:
			return list(self.tagdict.values())

	def put(self, tag, data):
		dp("[put] : %s, %s"%(self, tag))

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


def toggle_debug(toggle):
	global MODIO_DEBUG
	MODIO_DEBUG = toggle

def dp(msg):
	if MODIO_DEBUG:
		print(msg)

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
	datatype = type(data)

	# If the data block being validated is a list
	if datatype == list:

		# Run through the list to ensure it's only filled with uints
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
				raise UnknownDataType

		return data

	elif datatype == str:
		return [ord(c) for c in data]

	elif datatype == int:
		return [data]

	else:
		raise UnknownDataType

	return

def floatToRawLongBits(value):
	return struct.unpack('I', struct.pack('f', value))[0]

def doubleToRawLongBits(value):
	return struct.unpack('I', struct.pack('d', value))[0]

def longBitsToDouble(bits):
	return struct.unpack('d', struct.pack('I', bits))[0]

def shortBitsToFloat(bits):
	return struct.unpack('f', struct.pack('i', bits))[0]


#
#	Exceptions
#


class InvalidModioFormat(Exception):
	pass

class IncorrectModioVersion(Exception):
	pass

class ModioTagOverflow(Exception):
	pass

class UnknownDataType(Exception):
	pass

