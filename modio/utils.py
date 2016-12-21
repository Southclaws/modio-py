import struct


def _tag_StringToInt(s):
    if len(s) != 4:
        return 0

    return (
        (ord(s[0]) << 24) |
        (ord(s[1]) << 16) |
        (ord(s[2]) << 8) |
        (ord(s[3])))


def _tag_IntToString(i):
    s = []

    s.append(str(chr((i >> 24) & 0xFF)))
    s.append(str(chr((i >> 16) & 0xFF)))
    s.append(str(chr((i >> 8) & 0xFF)))
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

                # Run through string, grab each character integer and insert it
                pos = 0
                for char in d:
                    data.insert(i + pos, ord(char))
                    pos += 1

            elif datatype != int:
                raise ValueError

        return data

    elif datatype == str:
        return [ord(c) for c in data]

    elif datatype == int:
        return [data]

    else:
        raise ValueError

    return


def floatToRawLongBits(value):
    return struct.unpack('I', struct.pack('f', value))[0]


def doubleToRawLongBits(value):
    return struct.unpack('I', struct.pack('d', value))[0]


def longBitsToDouble(bits):
    return struct.unpack('d', struct.pack('I', bits))[0]


def shortBitsToFloat(bits):
    return struct.unpack('f', struct.pack('i', bits))[0]
