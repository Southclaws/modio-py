import pymodiolib as modio
import unittest


class ModioWriteTest(unittest.TestCase):

	def test_write(self):

		print("Declaring data\n")

		itag = "ITAG"
		idata = 42

		ftag = "FTAG"
		fdata = 88.142

		stag = "STAG"
		sdata = "This is my string data"

		print("Opening file\n")

		with modio.open("datafile.dat", "w") as m:
			print("Writing data\n")

			m.put(itag, idata)
			m.put(ftag, fdata)
			m.put(stag, sdata)

		print("Write operation complete\n")
		print("Reading data to verify it\n")

		with modio.open("datafile.dat", "r") as m:
			print("Reading data\n")

			ret_idata = m.get(itag)
			self.assertEqual(ret_idata.get_data(), [idata])

			ret_fdata = m.get(ftag)
			self.assertEqual(round(modio.shortBitsToFloat(ret_fdata.get_data()[0]), 3), fdata)

			ret_sdata = m.get(stag)
			self.assertEqual(ret_sdata.get_data(), [sdata])


if __name__ == '__main__':
	unittest.main()
