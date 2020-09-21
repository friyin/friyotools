#!/usr/bin/env python
import getopt
import json
import sys
import requests
import urllib3
import slugify as sl


def main():
    print("""
  ____                       _           _ 
 / ___|_ __ _   _ _ __   ___| |__   __ _| |
| |   | '__| | | | '_ \ / __| '_ \ / _` | |
| |___| |  | |_| | | | | (__| | | | (_| |_|
 \____|_|   \__,_|_| |_|\___|_| |_|\__,_(_)
                               by friyin""")
    print()

    user_key = None
    organization = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "k:o:", ["key=", "organization="])
    except getopt.GetoptError as err:
        print(str(err))
        print("Usage {argv[0]} -k key -o organization")
        sys.exit(1)

    for o, a in opts:
        if o in ("-k", "--key"):
            user_key = a
        elif o in ("-o", "--organization"):
            organization = a
        else:
            assert False, "unhandled option"

    if not user_key:
        print("Missing user key")
        sys.exit(1)

    if not organization:
        print("Missing organization")
        sys.exit(1)

    org_slug = sl.slugify(organization)
    #org_slug = 'oath_inc'

    page = 0
    count = 0

    print(f"Searching {organization} ({org_slug})")

    while True:
        page += 1
        url = f"https://api.crunchbase.com/v/3/organizations/{org_slug}/acquisitions?page={page}&user_key={user_key}"

        r = requests.get(url, timeout=10)

        data = json.loads(r.content.decode('utf-8'))
        if len(data) == 1:
            print(f"ERROR: Message: {data[0]['message']} Code: {data[0]['code']} Status {data[0]['status']}")
            break

        total_items = data['data']['paging']['total_items']
        if total_items == 0:
            print("/No items found")
            break

        if page == 1:
            print(f"Searching {organization}")
            print(f"Total items {total_items}")

        items = data['data']['items']

        if len(items) == 0:
            print("/End of search")
            break

        for item in items:
            count += 1
            uuid = item['uuid']

            print(f"Item #{count}")
            print()
            print(f" - Type: {item['type']}")
            print(f" - UUID: {uuid}")
            properties = item['properties']
            acquiree = item['relationships']['acquiree']['properties']
            print(f" - Acquisition Type: {properties['acquisition_type']}")
            print(f" - Acquisition Status: {properties['acquisition_status']}")
            print(f" - Acquiree Name: {acquiree['name']}")
            print(f" - Acquiree Description: {acquiree['short_description']}")
            if acquiree['founded_on']:
                print(f" - Acquiree Founded on: {acquiree['founded_on']}")
            if acquiree['homepage_url']:
                print(f" - Acquiree Homepage URL: {acquiree['homepage_url']}")

            print()
            print()




if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
