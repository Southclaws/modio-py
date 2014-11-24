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
		if os.path.splitext(args.input)[1] == ".json":
			print("input file is json, convert to modio")
			readJSON(args.input, args.output, args.tags)

		else:
			print("input file isn't json, try to read as modio")
			readModio(args.input, args.output, args.tags)

	else:
		parser.print_help()


def readJSON(inp, out, tags):
	data = {}

	with io.open(inp, "r") as f:
		data = json.loads(f.read())

	if not out:
		for num, k in enumerate(data):
			if tags:
				if k in tags:
					print("[%d/%d] tag:'%s',data:'%s'"%(num+1, len(data), k, data[k]))

			else:
				print("[%d/%d] tag:'%s',data:'%s'"%(num+1, len(data), k, data[k]))

	else:
		print("Writing JSON data to modio output...")

		with modio.open(out, "w") as m:
			for num, k in enumerate(data):
				if tags:
					if k in tags:
						m.put(k, data[k])

				else:
					m.put(k, data[k])


def readModio(inp, out, tags):
	data = []
	length = 0

	version = 0
	filesize = 0
	numtags = 0

	if tags:
		with modio.open(inp, "r") as m:
			version, filesize, numtags = m.metadata()
			for t in tags:
				data.append(m.get(t))

	else:
		with modio.open(inp, "r") as m:
			version, filesize, numtags = m.metadata()
			data = m.get()

	if not out:
		print("version:", version)
		print("file_size:", filesize)
		print("num_tags:", numtags)
		for num, i in enumerate(data):
			print("[%d/%d] tag:'%s',size:'%d',data:\n%s\n"%(num+1, len(data), i.get_name_str(), i.get_size(), i.get_data_format()))

	else:
		print("Writing modio data to JSON output...")

		data_dict = {}

		for i in data:
			data_dict[i.get_name_str()] = i.get_data_format()

		with io.open(out, "w") as f:
			f.write(json.dumps(data_dict, indent=4))


if __name__ == '__main__':
	main()
