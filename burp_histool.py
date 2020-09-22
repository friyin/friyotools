#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import base64


def main():
    xml = ET.parse('test.xml')
    item_list = xml.findall("item")

    root = xml.getroot()

    print(f'Exported with BURP Version {root.attrib["burpVersion"]} at {root.attrib["exportTime"]}')

    print(f"Found {len(item_list)} item/s")
    print()
    count = 0
    for item in item_list:
        count += 1
        print(f"Item {count}")
        time = item.find("time").text
        url = item.find("url").text
        extension = item.find("extension").text
        protocol = item.find("protocol").text
        port = item.find("port").text
        method = item.find("method").text

        host_item = item.find("host")

        host = host_item.text
        ip = host_item.attrib["ip"]

        print(f"Time: {time}")
        print(f"URL: {url}")
        print(f"Extension: {extension}")
        print(f"HOST: {host}")
        print("IP:", ip)
        print("Protocol:", protocol)
        print("Port:", port)
        print("Method:", method)

        request = base64.b64decode(item.find("request").text.encode("ascii")).decode("latin-1")
        request_lines = request.split('\r\n')

        print("Request:")
        #print(request)

        for line in request_lines:
            print("  - Line:", line)

        print()


if __name__ == '__main__':
    print("BURP History Tool for attack and profit")
    print("Options: CURL Export, Custom attack")

    print(" Custom attack options: Filter, Header inject, Message inject")
    main()

