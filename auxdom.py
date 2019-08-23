#!/usr/bin/env python3

import sys


def prepend_https(lines):
    for l in lines:
        l = l.strip().replace("https://", "").replace("http://", "").replace("*.", "").replace("*", "")

        if l.startswith("."):
            l = l[1:]

        print("https://%s" % l)


def filter_wildcard(lines):
    for l in lines:
        l = l.strip().replace("https://", "").replace("http://", "")

        if l.startswith("*.") or l.startswith("*"):
            l = l.replace(".*", "").replace("*", "")

            if l.startswith("."):
                l = l[1:]

            if l.endswith("/"):
                l = l[0:-1]

            print(l)



function = sys.argv[1]
domain_path = sys.argv[2]

if domain_path == '-':
    lines = sys.stdin.readlines()
else:
    with open(domain_path, "r") as f:
        lines = f.readlines()


if function == "s":
    prepend_https(lines)


if function == "w":
    filter_wildcard(lines)

