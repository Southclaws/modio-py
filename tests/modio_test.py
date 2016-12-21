import unittest
import io
import struct
import random
import os

import modio


class ModioWriteTest(unittest.TestCase):
    def test_write(self):
        tag1 = "SCAL"
        data1 = 42
        tag2 = "LIST"
        data2 = [97, 34, 85, 23, 99, 54, 33, 75]

        with modio.open("datafile.dat", "w") as m:
            m.put(tag1, data1)
            m.put(tag2, data2)

        with modio.open("datafile.dat", "r") as m:
            ret_data1 = m.get(tag1)
            self.assertEqual(ret_data1.get_data(), data1)

            ret_data2 = m.get(tag2)
            self.assertEqual(ret_data2.get_data(), data2)

        os.remove("datafile.dat")

    def test_bad_file(self):
        with io.open("badfile.dat", "wb") as f:
            data = [random.randint(32, 127) for _ in range(16)]
            f.write(struct.pack('16I', *data))

        with self.assertRaises(modio.exceptions.IncorrectModioVersion):
            with modio.open("badfile.dat", "r") as m:
                data = m.get("ATAG")

        os.remove("badfile.dat")


if __name__ == '__main__':
    unittest.main()
