
def parse_file(database, version, filetype, file):
    # we need to mark all previous versions as deleted, this files are always full loads
    statement = """
      UPDATE `rjis`.`toc`
          SET `deleted_version` = %s 
      WHERE `deleted_version` IS NULL
          AND `created_version` <> %s
      """

    values = (version, version)
    __execute_query(database, statement, values)

    statement = """
       UPDATE `rjis`.`fare_toc`
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
            if line[0:1] == 'T':
                __process_toc_line(database, version, filetype, line)
            if line[0:1] == 'F':
                __parse_toc_fare_toc_line(database, version, filetype, line)


def __process_toc_line(database, version, filetype, line):
    record = __parse_toc_line(line)
    __create_toc_record(database, version, record)


def __parse_toc_fare_toc_line(database, version, filetype, line):
    record = __parse_fare_toc_line(line)
    __create_fare_toc_record(database, version, record)


def __parse_toc_line(line):
    record = {
        "toc_id": line[1:3],
        "toc_name": line[3:33].strip(),
        "reservation_system": line[33:41].strip(),
        "active_indicator": 'yes' if line[41:42] == 'Y' else 'no'
    }

    return record


def __parse_fare_toc_line(line):
    record = {
        "fare_toc_id": line[1:4],
        "toc_id": line[4:6].strip(),
        "fare_toc_name": line[6:36].strip()
    }

    return record


def __create_toc_record(database, version, record):
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

    __execute_query(database, statement, values)

def __create_fare_toc_record(database, version, record):
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

    __execute_query(database, statement, values)


def __execute_query(database, statement, values):
    cursor = database.cursor()
    cursor.execute(statement, values)
    database.commit()
