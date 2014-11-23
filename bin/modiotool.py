import pymodiolib as modio
import io
import json
import logging
import argparse
import os


def main():

	logging.basicConfig(filename='modio_debug.log', level=logging.DEBUG)

	parser = argparse.ArgumentParser(description='Read and write modio format files.')

	parser.add_argument('--input', '-i',
		metavar='FILE', type=str,
		help='The input modio or json format file.')

	parser.add_argument('--tags', '-t',
		metavar='TAG', type=str, nargs='*',
		help='Specify one or more tags to read.')

	parser.add_argument('--output', '-o',
		metavar='FILE', type=str, nargs='?',
		help='The output json or modio format file.')

	args = parser.parse_args()

	if args.input:
		if os.path.splitext(args.input) == ".json":
			print("input file is json, convert to modio")
			readJSON(args.input, args.output, args.tags)

		else:
			print("input file isn't json, try to read as modio")
			readModio(args.input, args.output, args.tags)

	else:
		parser.print_help()


def readJSON(inp, out, tags):

	print("Reading JSON...")

	if not out:
		print("Dumping JSON to console...")

	else:
		print("Writing JSON data to modio output...")

		# m = modio.open("file.dat", modio.mode_write)
		# m.put("DATA", data)
		# m.close()


def readModio(inp, out, tags):

	data = []
	length = 0

	if tags:
		with modio.open(inp, 0) as m:
			for t in tags:
				data.append(m.get(t))

	else:
		with modio.open(inp, 0) as m:
			data = m.get()

	if not out:
		for num, i in enumerate(data):
			print("[%d/%d] tag:'%s',size:'%d',data:'%s'"%(num+1, len(data), i.getNameStr(), i.getSize(), i.getDataFormat()))

	else:
		serialised = {}

		for i in data:
			serialised[i.getNameStr()] = i.getDataFormat()

		with io.open(out, "w") as f:
			f.write(json.dumps(serialised, indent=4))



if __name__ == '__main__':
	main()
