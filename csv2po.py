"""
This script extracts all strings on Django's .po files and creates a CSV file with that content.

Usage: python csv2po.py <base_path> <input_file>
"""

import sys
import os
import fnmatch
import polib
import csv

#globals (Sigh!)

usage_string = "Usage: python csv2po.py <base_path> <input_file>"

#functions

def read_csv(path):
	"""
		Reads translations from the CSV file at the given path.

		:param path: the CSV file path
		:type path: string
		:return: the translations table
		:rtype: dictionary
		:raises: IOError if path is invalid
	"""
	if not os.path.exists(path):
		raise IOError("Invalid path: {0}.".format(path))

	#translations = []
	#with open(path, 'r') as csvfile:
	#	reader = csv.DictReader(csvfile)
	#	for row in reader:
	#		translations.append(row)

	translations = {}
	with open(path, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		headers = reader.fieldnames
		remove_set = set([headers.index('msgid'), headers.index('fuzzy?')])
		available_locales = [v for i, v in enumerate(headers) if i not in remove_set]
		for row in reader:
			message_id = row[headers[headers.index('msgid')]]
			message_data = []
			for locale in available_locales:
				message_data.append({locale: row[locale]})
			translations[message_id] = message_data;

	return translations

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

def merge_translations_to_file(translations, path):
	"""
		Merges the translations on the file at the given path.

		:param translations the translations table
		:type translations dictionary
		:param path the po file path
		:type path string
		:raises IOError if file does not exists, ValueError if translations is empty
	"""
	if not os.path.exists(path):
		raise IOError("Invalid path: {0}".format(path))

	if not len(translations):
		raise ValueError("Translations must not be empty.")

	locale = parse_locale(path)
	po = polib.pofile(path) 

	for entry in po:
		#import pdb; pdb.set_trace()
		message_data = translations[prepare_string(str(entry.msgid))]
		for item in message_data:
			message_string = item.get(locale)

			if message_string != None:
				entry.msgstr = message_string
		
	po.save()

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
	input_file = sys.argv[2]

	translations = read_csv(input_file)
	po_file_paths = find_files(base_path, 'po')

	for path in po_file_paths:
		merge_translations_to_file(translations, path)

	print("Done! Merged translations in {0} files.".format(len(po_file_paths)))
	exit(0)
