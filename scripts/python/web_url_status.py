#!/usr/bin/python3

# standard imports
import argparse

# lib imports
import requests
from requests.packages import urllib3

REQUESTS_TYPE = dict(
    get=requests.get,
    post=requests.post
)


def web_url_status():
    """Test the status of a web url."""
    if args.verify_disable:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = REQUESTS_TYPE[args.type.lower()](url=args.url, timeout=10, verify=not args.verify_disable)
    except (requests.exceptions.RequestException, requests.exceptions.RequestException):
        print('OFF')
    else:
        if response.status_code in [requests.codes.ok]:
            print('ON')
        else:
            print('OFF')


def main():
    web_url_status()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Test the status of a web service.",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-u', '--url', type=str, required=True, help='Full url to test.')
    parser.add_argument('-t', '--type', type=str, required=False, default='get', help='Request type. (get, post)')
    parser.add_argument('-v', '--verify_disable', action='store_true', help='Disable SSL verification.')

    args = parser.parse_args()

    main()
