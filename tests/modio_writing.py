import pymodiolib as modio
import io
import struct
import random
import unittest


class ModioWriteTest(unittest.TestCase):

	def test_write(self):

		print("Declaring data\n")

		tag1 = "SCAL"
		data1 = 42

		tag2 = "LIST"
		data2 = [97, 34, 85, 23, 99, 54, 33, 75]

		print("Opening file\n")

		with modio.open("datafile.dat", "w") as m:
			print("Writing data\n")

			m.put(tag1, data1)
			m.put(tag2, data2)

		print("Write operation complete\n")
		print("Reading data to verify it\n")

		with modio.open("datafile.dat", "r") as m:
			print("Reading data\n")

			ret_data1 = m.get(tag1)
			self.assertEqual(ret_data1.get_data(), data1)

			ret_data2 = m.get(tag2)
			self.assertEqual(ret_data2.get_data(), data2)

	def test_bad_file(self):

		print("Creating a bad file")

		with io.open("badfile.dat", "wb") as f:
			data = [random.randint(32, 127) for _ in range(16)]
			f.write(struct.pack('16I', *data))

		print("Trying to read data")

		with modio.open("badfile.dat", "r") as m:
			data = m.get("ATAG")

		print("Done.")


if __name__ == '__main__':
	unittest.main()
