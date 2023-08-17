#!/usr/bin/python3
"""
command_line:
  # sensors
  - sensor:
      name: Sindoh Percent Complete
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor percent_complete"
      unit_of_measurement: '%'
      scan_interval: 60
  - sensor:
      name: Sindoh Original Print Time
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor estimated_time_original"
      unit_of_measurement: 'min'
      scan_interval: 60
  - sensor:
      name: Sindoh Estimated Time Remaining
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor estimated_time_remaining"
      unit_of_measurement: 'min'
      scan_interval: 60
  - sensor:
      name: Sindoh Filament Color
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor filament_rgb"
      unit_of_measurement: 'RGB'
      scan_interval: 60
  - sensor:
      name: Sindoh Filament Material
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor filament_type"
      scan_interval: 60
  - sensor:
      name: Sindoh Bed Temperature
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor temperature_bed --units C"
      unit_of_measurement: '°C'
      scan_interval: 10
  - sensor:
      name: Sindoh Nozzle Temperature
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor temperature_nozzle --units C"
      unit_of_measurement: '°C'
      scan_interval: 10
  - sensor:
      name: Sindoh Filename
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor filename"
      scan_interval: 60
  - sensor:
      name: Sindoh Status Code
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_status --sensor printer_status_code"
      scan_interval: 60
  - sensor:
      name: Sindoh Camera Image
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_camera"
      scan_interval: 60
  - binary_sensor:
      name: Sindoh Printer
      command: "python3 /config/scripts/python/sindoh.py --ip x.x.x.x --command printer_sensor"
      scan_interval: 60
      payload_on: True
      payload_off: False
      scan_interval: 10
"""
# imports
import requests
import argparse

# from PIL import Image

if __name__ == '__main__':
    # argparse
    parser = argparse.ArgumentParser(description="Additional sensors for Sindoh 3d printers.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--ip', type=str, required=True, help='IP address of printer.')
    parser.add_argument('-c', '--command', type=str, required=True,
                        help='Command to execute. Options are printer_status, printer_cancel, printer_camera, '
                             'printer_sensor')
    parser.add_argument('-s', '--sensor', type=str, required=False, default='filename',
                        help='percent_complete, estimated_time_original, estiamted_time_remaining, filament_remaining, '
                             'filament_rgb, filament_type, temperature_bed, temperature_nozzle, filename, '
                             'printer_status_code')
    parser.add_argument('-n', '--units', type=str, required=False, default='C', help='F or C')
    args = parser.parse_args()

    # command urls
    cmd_printer_status = '/cgi-bin/config_periodic_data.cgi'
    cmd_printer_cancel = '/cgi-bin/cancel_job.cgi'
    cmd_printer_camera = '/?action=snapshot'

    # initialize session
    s = requests.Session()  # https://requests.readthedocs.io/en/master/user/advanced/#session-objects
    url_prefix = f'http://{args.ip}'

    # get printer status
    if args.command == 'printer_status' or args.command == 'printer_sensor':
        url = f'{url_prefix}{cmd_printer_status}'
        r = s.get(url)
        tmp = r.text

        tmp = tmp.split('(', 1)[-1].rsplit(')', 1)[0].split(',', 11)

        x = 0
        while x < len(tmp):
            tmp[x] = tmp[x].strip()
            x += 1

        sensor_dictionary = {
            'estimated_time_original': 0,
            'estimated_time_remaining': 'false',  # calculate from 0 and 2
            'printer_status_code': 1,
            'percent_complete': 2,
            'filament_remaining': 3,
            'filament_sub': 4,
            'filament_rgb': 'false',  # calculate from 5-7
            'filament_type': 8,
            'temperature_bed': 9,
            'temperature_nozzle': 10,
            'filename': 11
        }

        filament_dictionary = {
            '1': 'PLA',
            '2': 'ABS',
            '3': 'WOOD',
            '4': 'HIPS',
            '5': 'PETG',
            '13': 'ASA',
            '255': ' '
        }

        if sensor_dictionary[args.sensor] != 'false':
            tmp = tmp[sensor_dictionary[args.sensor]]

            if sensor_dictionary[args.sensor] == 0:
                tmp = int(int(tmp) / 60)
            if sensor_dictionary[args.sensor] == 2 or sensor_dictionary[args.sensor] == 3 or sensor_dictionary[args.sensor] == 4:
                pass
            elif args.sensor == 'filament_type':
                tmp = filament_dictionary[tmp]
            elif sensor_dictionary[args.sensor] == 9 or sensor_dictionary[args.sensor] == 10:
                if args.units == 'F':
                    tmp = int(tmp) * 1.8 + 32
                elif args.units == 'C':
                    tmp = int(tmp)
                else:
                    tmp = 'Units error'
                tmp = round(tmp, 1)  # https://www.w3schools.com/python/ref_func_round.asp
        elif sensor_dictionary[args.sensor] == 'false':
            if args.sensor == 'estimated_time_remaining':
                tmp = int((int(tmp[0]) * (1 - int(tmp[2]) * 0.01)) / 60)
            elif args.sensor == 'filament_rgb':
                tmp = f'{tmp[5], tmp[6], tmp[7]}'.replace("'", '')
        else:
            tmp = 'Sensor error'
        if args.command == 'printer_status':
            print(tmp)
        elif args.command == 'printer_sensor':
            if tmp == "''":
                tmp = False
            else:
                tmp = True
            print(tmp)
    # get camera image
    if args.command == 'printer_camera':
        url = f'{url_prefix}{cmd_printer_camera}'

        camera_filename = f'/local/sindoh/sindoh_camera_{args.ip.replace(".", "_")}.jpg'

        with open(camera_filename, 'wb') as handle:
            response = requests.get(url, stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

            # rotate = Image.open(camera_filename).rotate(270)
            print(camera_filename)

    # cancel print... need to test
    if args.command == 'printer_cancel':
        url = f'{url_prefix}{cmd_printer_cancel}'
        r = s.get(url)
