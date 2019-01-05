from os import walk
from zipfile import ZipFile
import zipfile
import re
import io
import time


def list_all_files(directory):
    # array to hold filenames
    files = []
    filteredfiles = []

    # regex for what we want
    regex = re.compile("RJFA([CF])([0-9]{3}).ZIP")

    # get all the files in the directory
    for (dirpath, dirnames, filenames) in walk(directory):
        files.extend(filenames)
        break

    # loop over the file names and match them all to regex
    for file in files:
        if re.match(regex, file):
            filteredfiles.append(file)

    return filteredfiles


def get_file_from_zip(zipfilename, filename_pattern):
    regex = re.compile(filename_pattern)

    if zipfile.is_zipfile(zipfilename):
        # open file in read only
        zfile = ZipFile(zipfilename, 'r')

        # list files in the zip file
        for name in zfile.namelist():
            if re.match(regex, name):
                zopen = zfile.open(name)
                return zopen
    else:
        print("Not a zip file")


def parse_headers(file):
    headers = {}

    header_regex = re.compile("^/!! ([a-zA-Z]+):\W+(.*)$")

    for line in io.TextIOWrapper(file):
        # strip the whitespace
        line = line.strip()

        if re.match(header_regex, line):
            matches = re.findall(header_regex, line)
            headers[matches[0][0]] =  matches[0][1]

    return headers


def sort_files(directory):
    files = list_all_files(directory)

    regex = re.compile("RJFA([CF])([0-9]{3}).ZIP")

    data_files = []

    for file in files:
        file_contents = get_file_from_zip(directory + "/" + file, "(.*).DAT")
        file_headers = parse_headers(file_contents)
        file_name = re.findall(regex, file)

        if file_name[0][0] == 'C':
            type = "changes"
        if file_name[0][0] == 'F':
            type = 'full'

        dict = {
            "date": file_headers['Generated'],
            "filename": file,
            "type": type

        }

        data_files.append(dict)

    # sort them by date
    data_files.sort(key=lambda x: time.mktime(time.strptime(x['date'], '%d/%m/%Y')))

    return data_files


def find_starting_point(data_files, mode):
    # find the last 'full' update, then return that and everything after it

    if mode == 'full':
        for index, value in enumerate(data_files):
            if value['type'] == 'full':
                s = slice(index, len(data_files))
                return data_files[s]

    if mode == 'latest':
        full_imports = []
        for index, value in enumerate(data_files):
            if value['type'] == 'full':
                full_imports.append(index)

        s = slice(full_imports[-1], len(data_files))
        return data_files[s]



def process(directory):
    data_files = sort_files(directory)
    starting_point = find_starting_point(data_files, 'latest')

    print(starting_point)