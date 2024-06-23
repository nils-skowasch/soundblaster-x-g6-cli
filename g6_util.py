def read_payload_as_hex_lines(payload_file_path):
    """
    Read the hex data from a payload text file as list, omitting any line separators
    :param payload_file_path: the file path to the payload hex-line file
    :return: the stripped file content lines as list
    """
    with open(payload_file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]
