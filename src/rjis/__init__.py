from os import walk
from zipfile import ZipFile
import zipfile
import re
import io
import time
import mysql.connector


# connect to the mysql database
database = mysql.connector.connect(
    host="localhost",
    user="user",
    passwd="password"
)


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

                lines = []
                for line in io.TextIOWrapper(zopen):
                    lines.append(line)

                return lines
    else:
        print("Not a zip file")

def list_files_in_zip(zipfilename):
    if zipfile.is_zipfile(zipfilename):
        # open file in read only
        zfile = ZipFile(zipfilename, 'r')

        # list files in the zip file
        return zfile.namelist()


def parse_headers(file):
    headers = {}

    header_regex = re.compile("^/!! ([a-zA-Z\W]+):\W+(.*)$")

    for line in file:
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


def process_file(zipfile, version, load_type):
    contents = list_files_in_zip(zipfile)


    for file_name in contents:
        file = get_file_from_zip(zipfile, file_name)
        headers = parse_headers(file)
        for line in file:
            process_line(headers['Content type'], line, version, load_type)

def process_line(type,line, version, load_type):
    if line[0:1] != '/':
        if type == 'TOC':
            if line[0:1] == 'T':
                parse_file_toc_toc_line(line, version)
            if line[0:1] == 'F':
                parse_file_toc_fare_toc_line(line, version)

        if type == 'LOC':
            if line[1:2] == 'L':
                parse_file_location_location_line(line, version, load_type)




def process(directory, load_type):
    data_files = sort_files(directory)
    files_to_process = find_starting_point(data_files, load_type)

    for file in files_to_process:
        version = create_version(file)

        if version:
            print("Importing {0}".format(file['filename']))
            process_file(directory + '/' + file['filename'], version, load_type)
        else:
            print("File {0} is already loaded".format(file['filename']))


def create_version(file):
    cursor = database.cursor(buffered=True)

    # firstly, let's check if this has already been imported
    statement = """
    SELECT `id` 
        FROM `rjis`.`versions` 
        WHERE 
            `filename` = %s AND 
            `version_date` = STR_TO_DATE(%s, '%d/%m/%Y') 
        LIMIT 1;
    """
    values = (file['filename'], file['date'])

    cursor.execute(statement, values)

    if cursor.rowcount == 0:
        cursor = database.cursor()

        statement = """
        INSERT INTO `rjis`.`versions` 
            (
                `filename`,
                `version_date`,
                `loaded_date`,
                `active_date`
            ) 
            VALUES (
                %s,
                TIMESTAMP(STR_TO_DATE(%s, '%d/%m/%Y')),
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP);
        """
        values = (file['filename'], file['date'])

        cursor.execute(statement, values)
        database.commit()

        return cursor.lastrowid
    else:
        return False


def parse_file_toc_toc_line(line, version):
    record = {
        "toc_id": line[1:3],
        "toc_name": line[3:33].strip(),
        "reservation_system": line[33:41].strip(),
        "active_indicator": 'yes' if line[41:42] == 'Y' else 'no'
    }

    # we need to mark all previous versions as deleted
    cursor = database.cursor()
    statement = """
    UPDATE `rjis`.`toc`
        SET `deleted_version` = %s 
    WHERE `deleted_version` IS NULL
        AND `created_version` <> %s
    """

    values = (version, version)
    cursor.execute(statement, values)

    statement = """
    INSERT INTO `rjis`.`toc` 
        (
            `toc_id`,
            `toc_name`,
            `reservation_system`,
            `active`,
            `created_version`
        )  
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s
        );
    """
    values = (record['toc_id'], record['toc_name'], record['reservation_system'], record['active_indicator'], version)
    cursor.execute(statement, values)

    database.commit()



def parse_file_toc_fare_toc_line(line, version):
    record = {
        "fare_toc_id": line[1:4],
        "toc_id": line[4:6].strip(),
        "fare_toc_name": line[6:36].strip()
    }

    # we need to mark all previous versions as deleted
    cursor = database.cursor()
    statement = """
    UPDATE `rjis`.`fare_toc`
        SET `deleted_version` = %s
    WHERE `deleted_version` IS NULL
        AND `created_version` <> %s
    """

    values = (version, version)
    cursor.execute(statement, values)

    statement = """
    INSERT INTO `rjis`.`fare_toc` 
        (
            `fare_toc_id`,
            `toc_id`,
            `fare_toc_name`,
            `created_version`
        )  
        VALUES (
            %s,
            %s,
            %s,
            %s
        );
    """
    values = (
        record['fare_toc_id'], record['toc_id'], record['fare_toc_name'], version)
    cursor.execute(statement, values)

    database.commit()

def parse_file_location_location_line(line, version, load_type):
    record = {
        "update_marker": line[0:1].strip(),
        "record_type": line[1:2].strip(),
        "uic_code": line[2:9].strip(),
        "end_date": line[9:17].strip(),
        "start_date": line[17:25].strip(),
        "quote_date": line[25:33].strip(),
        "admin_area_code": line[33:36].strip(),
        "nlc": line[36:40].strip(),
        "description": line[40:56].strip(),
        "crs_code": line[56:59].strip(),
        "resv_code": line[59:64].strip(),
        "ers_country": line[64:66].strip(),
        "ers_code": line[66:69].strip(),
        "fare_group": line[69:75].strip(),
        "county": line[75:77].strip(),
        "pte_code": line[77:79].strip(),
        "zone_no": line[79:83].strip(),
        "zone_ind": line[83:85].strip(),
        "region": line[85:86].strip(),
        "hierarchy": line[86:87].strip(),
        "cc_desc_out": line[87:128].strip(),
        "cc_desc_rtn": line[128:144].strip(),
        "atb_desc_out": line[144:204].strip(),
        "atb_desc_rtn": line[204:234].strip(),
        "special_facilities": line[234:260].strip(),
        "lul_direction_ind": line[260:261].strip(),
        "lul_uts_mode": line[261:262].strip(),
        "lul_zone_1": line[262:263].strip(),
        "lul_zone_2": line[263:264].strip(),
        "lul_zone_3": line[264:265].strip(),
        "lul_zone_4": line[265:266].strip(),
        "lul_zone_5": line[266:267].strip(),
        "lul_zone_6": line[267:268].strip(),
        "lul_uts_london_stn": int(line[268:269]),
        "uts_code": line[269:272].strip(),
        "uts_a_code": line[272:275].strip(),
        "uts_ptr_bias": line[275:276].strip(),
        "uts_offset": line[276:277].strip(),
        "uts_north": line[277:280].strip(),
        "uts_east": line[280:283].strip(),
        "uts_south": line[283:286].strip(),
        "uts_west": line[286:289].strip()
    }

    cursor = database.cursor()

    if load_type == 'full':
        statement = """
            UPDATE `rjis`.`location`
                SET `deleted_version` = %s;
        """

    if record['update_marker'] == 'I':
        statement = """
        INSERT INTO `rjis`.`location` 
            (
                `uic_code`,
                `end_date`,
                `start_date`,
                `quote_date`,
                `admin_area_code`,
                `nlc`,
                `description`,
                `crs_code`,
                `resv_code`,
                `ers_country`,
                `ers_code`,
                `fare_group`,
                `county`,
                `pte_code`,
                `zone_no`,
                `zone_ind`,
                `region`,
                `hierarchy`,
                `cc_desc_out`,
                `cc_desc_rtn`,
                `atb_desc_out`,
                `atb_desc_rtn`,
                `special_facilities`,
                `lul_direction_ind`,
                `lul_uts_mode`,
                `lul_zone_1`,
                `lul_zone_2`,
                `lul_zone_3`,
                `lul_zone_4`,
                `lul_zone_5`,
                `lul_zone_6`,
                `lul_uts_london_stn`,
                `uts_code`,
                `uts_a_code`,
                `uts_ptr_bias`,
                `uts_offset`,
                `uts_north`,
                `uts_east`,
                `uts_south`,
                `uts_west`,
                `created_version`
            )  
            VALUES (
                %s,
                STR_TO_DATE(%s, '%d%m%Y'),
                STR_TO_DATE(%s, '%d%m%Y'),
                STR_TO_DATE(%s, '%d%m%Y'),
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
        """
        values = (
            record['uic_code'],
            record['end_date'],
            record['start_date'],
            record['quote_date'],
            record['admin_area_code'],
            record['nlc'],
            record['description'],
            record['crs_code'],
            record['resv_code'],
            record['ers_country'],
            record['ers_code'],
            record['fare_group'],
            record['county'],
            record['pte_code'],
            record['zone_no'],
            record['zone_ind'],
            record['region'],
            record['hierarchy'],
            record['cc_desc_out'],
            record['cc_desc_rtn'],
            record['atb_desc_out'],
            record['atb_desc_rtn'],
            record['special_facilities'],
            record['lul_direction_ind'],
            record['lul_uts_mode'],
            record['lul_zone_1'],
            record['lul_zone_2'],
            record['lul_zone_3'],
            record['lul_zone_4'],
            record['lul_zone_5'],
            record['lul_zone_6'],
            record['lul_uts_london_stn'],
            record['uts_code'],
            record['uts_a_code'],
            record['uts_ptr_bias'],
            record['uts_offset'],
            record['uts_north'],
            record['uts_east'],
            record['uts_south'],
            record['uts_west'],
            version
        )

        cursor.execute(statement, values)

        database.commit()

    if record['update_marker'] == 'D':
        statement = """
            UPDATE `rjis`.`location`
                SET `deleted_version` = %s
            WHERE
                `uic_code` = %s AND
                `end_date` = STR_TO_DATE(%s, '%d%m%Y');
        """

        values = (version, record['uic_code'], record['end_date'])

        print ("Deleting location record")

        cursor.execute(statement, values)
        database.commit()