"""
# sensors for temperature and battery
sensor:
  - platform: command_line
    name: Door1 Temperature
    command: "python3 /config/scripts/python/gogogate.py --ip x.x.x.x --user YOURUSERNAME --password YOURPASSWORD --command door_status --door 1 --sensor temperature --units F"
    unit_of_measurement: '°F'
    scan_interval: 60
  - platform: command_line
    name: Door1 Battery
    command: "python3 /config/scripts/python/gogogate.py --ip x.x.x.x --user YOURUSERNAME --password YOURPASSWORD --command door_status --door 1 --sensor battery"
    unit_of_measurement: '%'
    scan_interval: 60

# switch to control the light on the hub and check the status
switch:
  - platform: command_line
    switches:
      gogogate_light:
        friendly_name: Gogogate Light
        command_on: "python3 /config/scripts/python/gogogate.py --ip x.x.x.x --user YOURUSERNAME --password YOURPASSWORD --command light_on"
        command_off: "python3 /config/scripts/python/gogogate.py --ip x.x.x.x --user YOURUSERNAME --password YOURPASSWORD --command light_off"
        command_state: "python3 /config/scripts/python/gogogate.py --ip x.x.x.x --user YOURUSERNAME --password YOURPASSWORD --command light_status"
        value_template: '{{ value == "1" }}'
"""
# imports
import requests
import argparse
import re

if __name__ == '__main__':
    # argparse
    parser = argparse.ArgumentParser(
        description="Additional sensors and switches for Gogogate2 hub. Do you not use any quotes when entering arguments.",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--ip', type=str, nargs=1, required=True,
                        help='URL of website... do not include http:// or /index.php')
    parser.add_argument('-u', '--user', type=str, nargs=1, required=False, default=['admin'],
                        help='Username for logging into hub wesbite')
    parser.add_argument('-p', '--password', type=str, nargs=1, required=True,
                        help='Password for logging into hub wesbite')
    parser.add_argument('-c', '--command', type=str, nargs=1, required=True,
                        help='Command to execute. Options are light_status, light_on, light_off, door_status, door_operate')
    parser.add_argument('-d', '--door', type=int, nargs=1, required=False, default=[1],
                        help='Door number... 1, 2, or 3')
    parser.add_argument('-m', '--move', type=int, nargs=1, required=False, default=[0],
                        help='Beta function... integer required 0 = toggle, 1 = open, 2 = close... all options seem to toggle the door')
    parser.add_argument('-s', '--sensor', type=str, nargs=1, required=False, default=['temperature'],
                        help='temperature or battery')
    parser.add_argument('-n', '--units', type=str, nargs=1, required=False, default=['F'], help='F or C')
    opts = parser.parse_args()

    # arguments to variables
    ip = opts.ip[0]
    user = opts.user[0]
    password = opts.password[0]
    command = opts.command[0]
    door = str(opts.door[0])
    move = str(opts.move[0])
    sensor = opts.sensor[0]
    units = opts.units[0]

    # command urls
    cmd_door_status = '/isg/temperature.php?door=' + door
    cmd_light_status = '/isg/light.php?op=refresh'
    cmd_light_on = '/isg/light.php?op=activate&light=0'
    cmd_light_off = '/isg/light.php?op=activate&light=1'
    cmd_door_operate = '/isg/opendoor.php?numdoor=' + door + '&status=' + move

    # initialize session
    s = requests.Session()  # https://requests.readthedocs.io/en/master/user/advanced/#session-objects
    url_prefix = 'http://' + ip
    url_suffix = '/index.php'
    url = url_prefix + url_suffix
    payload = {'login': user, 'pass': password,
               'send-login': 'Sign+In'}  # https://stackoverflow.com/a/28628514/11214013
    s.post(url, data=payload)
    r = s.get(url)

    # get light status
    if command == 'light_status':
        url = url_prefix + cmd_light_status
        r = s.get(url)
        print(r.text)
    # turn light on
    if command == 'light_on':
        url = url_prefix + cmd_light_on
        r = s.get(url)
    # turn light off
    if command == 'light_off':
        url = url_prefix + cmd_light_off
        r = s.get(url)
    # get door status
    if command == 'door_status':
        url = url_prefix + cmd_door_status
        r = s.get(url)
        tmp = re.findall('"([^"]*)"', r.text)  # https://stackoverflow.com/a/2076356/11214013
        # print(r.text)

        if sensor == 'temperature':
            tmp = int(tmp[0])
            tmp = tmp / 1000

            if units == 'F':
                tmp = tmp * 1.8 + 32
            elif units == 'C':
                pass
            else:
                tmp = 'Units error'
            tmp = round(tmp, 1)  # https://www.w3schools.com/python/ref_func_round.asp
        elif sensor == 'battery':
            tmp = int(tmp[1])
        else:
            tmp = 'Sensor error'
        print(tmp)
    # beta... seems to toggle the door no matter what
    if command == 'door_operate':
        url = url_prefix + cmd_door_operate
        r = s.get(url)
