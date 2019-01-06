
def parse_file(database, version, filetype, file):
    if filetype == 'full':
        # we need to mark all previous versions as deleted
        statement = """
                   UPDATE `rjis`.`toc`
                       SET `deleted_version` = %s 
                   WHERE `deleted_version` IS NULL
                       AND `created_version` <> %s
                   """

        values = (version, version)
        __execute_query(database, statement, values)

    for line in file:
        # if this isnt a comment
        if line[0:1] != '/':
            # if this is a location record
            if line[1:2] == 'L':
                __process_location_line(database, version, filetype, line)


def __process_location_line(database, version, filetype, line):
    # parse the line into a record
    record = __parse_location_line(line)

    # insert and refresh records are the same
    if record['update_marker'] == 'I' or record['update_marker'] == 'R':
        __create_location_record(database, version, record)

    # for delete records
    if record['update_marker'] == 'D':
        __delete_location_record(database, version, record)

    # for update record
    if record['update_marker'] == 'U':
        __delete_location_record(database, version, record)
        __create_location_record(database, version, record)


def __create_location_record(database, version, record):
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

    __execute_query(database, statement, values)


def __delete_location_record(database, version, record):
    statement = """
                UPDATE `rjis`.`location`
                    SET `deleted_version` = %s
                WHERE
                    `uic_code` = %s AND
                    `end_date` = STR_TO_DATE(%s, '%d%m%Y');
            """

    values = (version, record['uic_code'], record['end_date'])

    __execute_query(database, statement, values)


def __parse_location_line(line):
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

    return record


def __execute_query(database, statement, values):
    cursor = database.cursor()
    cursor.execute(statement, values)
    database.commit()
