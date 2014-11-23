import io
import struct
import logging


class ModioFileTag:

	def __init__(self, tag, data):
		self.tag = tag
		self.data = data


	def getData(self):
		return self.data


	def getSize(self):
		return len(self.data)


	def getTag(self):
		return self.tag


	def getTagAsInt(self):
		return self.tag



class ModioSession:

	def __init__(self, filename):
		logging.debug("__init__: %s"%(self))

		self.filename = filename

	def __enter__(self):
		logging.debug("__enter__: %s"%(self))

		self.readStack = []

		self.filever = 0
		self.filelen = 0
		self.numtags = 0
		self.taglist = {}

		try:
			filehandle = io.open(self.filename, "rb")

		except ValueError:
			return 0

		filedata = filehandle.read()
		fmat = "<%dI" % (len(filedata) // 4)
		self.readStack = list(struct.unpack(fmat, filedata))

		filehandle.close()

		self.filever = self.readStack[0]
		self.filelen = self.readStack[1]
		self.numtags = self.readStack[2]

		head_pointer = 3

		for i in range(self.numtags):

			tagname = self.readStack[head_pointer]
			physpos = self.readStack[head_pointer + 1]
			tagsize = self.readStack[3 + (self.numtags * 2) + physpos + 1]
			tagdata = self.readStack[3 + (self.numtags * 2) + physpos + 2 : (3 + (self.numtags * 2) + physpos + 2 + tagsize)]

			self.taglist[_tag_IntToString(tagname)] = ModioFileTag(tagname, tagdata)

			head_pointer += 2

		return self


	def __exit__(self, *err):
		logging.debug("__exit__: %s, %s"%(self, err))
		self.close()


	def close(self):
		logging.debug("close: %s"%(self))
		return


	def get(self, tag):
		logging.debug("get: %s, %s"%(self, tag))
		return self.taglist[tag].getData(), self.taglist[tag].getSize()


	def put(self, tag):
		logging.debug("put: %s, %s"%(self, tag))
		return



def open(filename, mode):

	m = ModioSession(filename)
	return m


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
