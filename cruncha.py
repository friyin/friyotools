#!/usr/bin/env python
import getopt
import json
import sys
import requests
import slugify as sl


def usage():
        print("Usage: {argv[0]} -k key -o organization [-u] [-r level]")
        print("       -k user_key")
        print("       -o organization to search")
        print("       -u (Optional) Show URLs only")
        print("       -r <number> (Optional) Recursion level (0=infinte) (Use with care!)")
        print()
        print(f"Example: {sys.argv[0]} -k 4579384534 -o yahoo")
        print()


def banner():
    print("""
  ____                       _           _ 
 / ___|_ __ _   _ _ __   ___| |__   __ _| |
| |   | '__| | | | '_ \ / __| '_ \ / _` | |
| |___| |  | |_| | | | | (__| | | | (_| |_|
 \____|_|   \__,_|_| |_|\___|_| |_|\__,_(_)
                               by friyin""")
    print()


class Cruncha:
    def __init__(self):
        self.user_key = None
        self.organization = None
        self.urls_only = False
        self.recursion_level = -1

        try:
            opts, args = getopt.getopt(sys.argv[1:], "k:o:ur:", ["key=", "organization=", "urls-only", "recursion-level="])
        except getopt.GetoptError as err:
            print(str(err))
            usage()
            sys.exit(1)

        for o, a in opts:
            if o in ("-k", "--key"):
                self.user_key = a
            elif o in ("-o", "--organization"):
                self.organization = a
            elif o in ("-u", "--urls-only"):
                self.urls_only = True
            elif o in ("-r", "--recursion-level"):
                self.recursion_level = int(a)

    def _get_v31_organizations_relationship(self, permalink, relationship, page=1):

        return f"https://api.crunchbase.com/v3.1/organizations/{permalink}/{relationship}?page={page}&user_key={self.user_key}"


    def execute(self):
        if not self.user_key:
            banner()
            print("ERROR: Missing user key (use -k)")
            print()
            usage()
            sys.exit(1)

        if not self.organization:
            banner()
            print("ERROR: Missing organization (use -o)")
            print()
            usage()
            sys.exit(1)


        if not self.urls_only:
            banner()
            print(f"Searching {self.organization}")

        permalink = sl.slugify(self.organization)
        self._get_acquisitions_by_org(permalink, rec=0)


    def _get_acquisitions_by_org(self, parent_permalink, rec=0):
        if self.recursion_level > 0 and rec > self.recursion_level:
            return

        count = 0
        page = 0

        while True:
            page += 1
            url = self._get_v31_organizations_relationship(parent_permalink, 'acquisitions', page)

            r = requests.get(url, timeout=10)

            data = json.loads(r.content.decode('utf-8'))
            if len(data) == 1:
                print(f"ERROR: Message: {data[0]['message']} Code: {data[0]['code']} Status {data[0]['status']}")
                break

            total_items = data['data']['paging']['total_items']
            if total_items == 0:
                if not self.urls_only:
                    print("/No items found")
                break

            if not self.urls_only and page == 1:
                print(f"Searching {parent_permalink} Total items: {total_items} Recursion level: {rec}")

            items = data['data']['items']

            if not len(items):
                if not self.urls_only:
                    print("/End of search")
                break

            for item in items:
                count += 1
                item_uuid = item['uuid']
                properties = item['properties']
                acquiree = item['relationships']['acquiree']['properties']

                if self.urls_only:
                    if acquiree['homepage_url']:
                        print(acquiree['homepage_url'])
                else:
                    print(f"Item #{count} (Recursion level: {rec})")
                    print(f" - Type: {item['type']}")
                    print(f" - UUID: {item_uuid}")
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

                if self.recursion_level >= 0:
                    self._get_acquisitions_by_org(acquiree['permalink'], rec + 1)


if __name__ == '__main__':
    c = Cruncha()
    c.execute()
