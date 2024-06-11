from __future__ import print_function
import sys
from os import path
import struct
from datetime import datetime
from binascii import hexlify
from time import strftime, localtime, sleep

def tee (file, data):
    file.write(data)
    sys.stdout.write(data)

def unpack(fmt, data):
    size = struct.calcsize(fmt)
    parsed_tuple = struct.unpack(fmt, data[:size])
    del data[:size]
    return parsed_tuple

def parse_tcp_imei(input):
    raw_packet = input
    (imei_len,) = unpack('!H', raw_packet)
    imei = int(raw_packet[:imei_len].decode("ascii"))
    del raw_packet[:imei_len]
    if len(raw_packet):
        print('Err data leftover')
    return imei

def parse_bin_file(input_filepath):
    raw_packet = 0
    with open(input_filepath, "rb") as f:
        raw_packet = bytearray(f.read())
    print("type: " + str(type(raw_packet)))
    imei = str(parse_tcp_imei(raw_packet))
    current_time = strftime("%Y-%m-%d %H-%M-%S", localtime())
    input_file = path.splitext(input_filepath)[0]
    filename = "{0}_{1}_{2}{3}".format(input_file, imei, current_time, ".csv")
    # current_time + imei + '.csv'
    first_data = path.exists(filename)
    with open(filename, 'a') as recordfile:
        if not first_data:
            header = 'date;timestamp;priority;longitude;latitude;altitude;angle;satellites;speed;evt_id;total_io\r'
            recordfile.write(header)
            print(header)
        try:
            parsed_io_list = list()
            print(hexlify(raw_packet))
            while len(raw_packet):
            # for rec in range(0, nod1):
                parsed_io_list.clear()
                timestamp, priority, longitude, latitude, altitude, angle, sats, speed = unpack('!QBIIHHBH', raw_packet)
                date = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
                evt_io_id, total_io_num = unpack('!BB', raw_packet)
                (one_byte_io,) = unpack('!B', raw_packet)
                for idx in range(0, one_byte_io):
                    io_id, io_value = unpack('!BB', raw_packet)
                    parsed_io_list.append({
                        'io_id' : io_id,
                        'io_value' : io_value
                    })
                (two_byte_io,) = unpack('!B', raw_packet)
                for idx in range(0, two_byte_io):
                    io_id, io_value = unpack('!BH', raw_packet)
                    parsed_io_list.append({
                        'io_id' : io_id,
                        'io_value' : io_value
                    })
                (four_byte_io,) = unpack('!B', raw_packet)
                for idx in range(0, four_byte_io):
                    io_id, io_value = unpack('!BI', raw_packet)
                    parsed_io_list.append({
                        'io_id' : io_id,
                        'io_value' : io_value
                    })
                (eight_byte_io,) = unpack('!B', raw_packet)
                for idx in range(0, eight_byte_io):
                    io_id, io_value = unpack('!BQ', raw_packet)
                    parsed_io_list.append({
                        'io_id' : io_id,
                        'io_value' : io_value
                    })
                """
                (var_size_io,) = unpack('!H', raw_packet)
                for idx in range(0, var_size_io):
                    io_id, io_len = unpack('!HH', raw_packet)
                    io_value = hexlify(raw_packet[:io_len])
                    del raw_packet[:io_len]
                    parsed_io_list.append({
                        'io_id': io_id,
                        'io_value': io_value
                    })
                """
                tee(recordfile, '{0};{1};{2};{3};{4};{5};{6};{7};{8};'.format(date, timestamp, priority, longitude, latitude, altitude, angle, sats, speed))
                tee(recordfile, '{0};{1};'.format(evt_io_id, total_io_num))
                for io in parsed_io_list:
                    tee(recordfile, '{0}:{1};'.format(io['io_id'], io['io_value']))
                tee(recordfile, "\n")
        except:
            print('Err corrupted packet')

def main():
    print('c8e_bin_parser Ver.1.1')
    file_list = list()
    for arg in sys.argv[1:]:
        if path.exists(arg) :
            file_list.append(arg)
    for file in file_list:
        parse_bin_file(file);


if __name__ == "__main__":
   main()