"""
This script extracts all strings on Django's .po files and creates a CSV file with that content.

Usage: python3 po2csv.py <base_path> <output_file>"
"""

import sys
import os
import fnmatch
import polib
import csv

#globals (Sigh!)

usage_string = "Usage: python3 po2csv.py <base_path> <output_file>"

#functions

def find_files(path,extension):
	"""
		Find files with the given extension under the given path.

		:param path: base path
		:type path: string
		:param extension: file extension
		:type extension: string
		:return: paths to the files with the provided extension under the given path
		:rtype: list
		:raises: IOError if path doesn't exist
	"""
	if not os.path.exists(path):
		raise IOError("Invalid path: {0}".format(path))

	po_file_paths = []
	for root, dir, files in os.walk(path):
		for f in files:
			if fnmatch.fnmatch(f, "*.{0}".format(extension)):
				po_file_paths.append(os.path.join(root, f))

	return po_file_paths

def parse_locales(paths):
	"""
		Extracts the locales from the given paths.

		:param paths: the paths
		:type path: list
		:return: the locales 
		:rtype: set
		:raises: ValueError if paths is empty
	"""

	if not paths:
		raise ValueError("Invalid argument: no paths were passed.")

	return set([parse_locale(path) for path in paths])
	
def parse_locale(path):
	"""
		Extracts the locale from the given path.
		Assumes a django-esque path structure of: <base_path>/app/locale/<locale_id>/LC_MESSAGES/<file.po>

		:param path: the path
		:type path: string
		:return: the locale
		:rtype: string
		:raises: IOError if path doesn't exist
		:raises: IndexError if path doesn't have the expected structure
	"""

	if not os.path.exists(path):
		raise IOError("Invalid path: {0}".format(path))

	path_list = path.split(os.sep)
	locale = path_list[-3]
	return locale

def print_list_one_per_line(list):
	"""
		Prints the given list, one element per line.

		:param list: the list to print
		:type list: list 
		:raises: TypeError: if list doesn't contains strings
	"""

	print("\n".join(list))

def extract_translation_entries(path):
	"""
		Extracts the translation entries from the file at the given path.

		:param path: the translation file path
		:type path: string
		:return a dictionary with translation entries
		:rtype: dictionary
		:raises: IOError: if path doesn't exists
	"""

	if not os.path.exists(path):
		raise IOError("Invalid path: {0}".format(path))

	result = {}
	po = polib.pofile(path)
	for entry in po:
		is_fuzzy = 'fuzzy' in entry.flags
		result[entry.msgid] = [entry.msgstr, is_fuzzy]

	return result

def build_translation_table(paths):
	"""
		Builds the translation table.
		The translation table is a dictionary keyed by message id. The value is the pair <locale, message string>.

		:param paths: the paths to translation files
		:type paths: list
		:return the translations table
		:rtype: dictionary
		:raises: ValueError: if paths is empty
	"""
	if not paths:
		raise ValueError("Invalid argument: no paths were passed.")

	table = {}
	for path in paths:
		locale = parse_locale(path)
		translations = extract_translation_entries(path)
		for key, value in translations.items():
			if not table.get(key):
				table[key] = [{locale:value}]
			else:				
				table[key].append({locale:value})
	return table

def write_to_csv_file(headers, table, out_file_path):
	"""
		Writes the data to the CSV file at the given path.

		:param headers: the headers
		:type headers: list
		:param table: the translation table
		:type table: dictionary
		:param out_file_path: the output file path
		:type out_file_path: string
		:raises: ValueError: if headers or table are empty
	"""

	if len(headers) == 0:
		raise ValueError("Invalid argument: no headers were passed.")

	if len(table) == 0:
		raise ValueError("Invalid argument: translation table does not contain entries.")

	with open(out_file_path, 'w', encoding='utf-8') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=headers)
		writer.writeheader()
		for msgid in sorted(table):
			line = build_csv_line(msgid, table[msgid], headers)
			writer.writerow(line)

def build_csv_line(message_id, message_data, headers):
	"""
		Build a CSV line with the given message ID and data.

		:param message_id: the message ID
		:type message_id: string
		:param message_data: the message data
		:type message_data: dictionary
		:param headers: the headers
		:type headers: list
		:return: the CSV line
		:rtype: dictionary
		:raises: ValueError: if message_id, message_data or headers are empty.
	"""
	if len(message_id) == 0:
		raise ValueError("Invalid argument: message ID is empty.")

	if len(message_data) == 0:
		raise ValueError("Invalid argument: no message data was passed.")

	if len(headers) <= 2:
		raise ValueError("Invalid argument: headers size was {0} and it should have been > 2.".format(len(headers)))

	line = {headers[0]:prepare_string(message_id)}
	for entry in message_data:
		for locale,translation_info in entry.items():
			line[headers[1]] = '*' if translation_info[1] == True else ''
			line[locale] = prepare_string(translation_info[0])

	return line

def prepare_string(s):
	"""
		Prepares the string for the desired output format (keeping \n chars and trimming the trailing and leading quotes).

		:param str: the string
		:type str: string
		:return: the string in the desired output format
		:rtype: string
	"""
	return repr(s)[1:-1]

def exit_with_message(message):
	"""
		Prints the give message and exits.

		:param message: the message
		:type message: string
	"""

	print(message)
	exit(-1)
 
#script body

if __name__ == '__main__':

	# Check arguments
	args_len = len(sys.argv)

	if args_len < 3:
		exit_with_message("Invalid number of arguments.\n{}".format(usage_string))

	base_path = sys.argv[1]
	output_file = sys.argv[2]

	po_file_paths = find_files(base_path,'po')

	headers = ['msgid', 'fuzzy?']
	for locale in parse_locales(po_file_paths):
		headers.append(locale)

	table = build_translation_table(po_file_paths)

	write_to_csv_file(headers, table, output_file)

	print("Done! Processed {0} translation files.".format(len(po_file_paths)))
	exit(0)
