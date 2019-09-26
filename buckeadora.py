#!/usr/bin/env python3

import sys, requests, getopt, boto3, botocore
from html.parser import HTMLParser

from botocore.exceptions import ClientError

USAGE_HELP = """
Usage:
  %s -d domain
"""

class StringToSignParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active_tag = False
        self.data = None


    def handle_starttag(self, tag, attrs):
        if tag == 'stringtosign':
            self.active_tag = True

    def handle_endtag(self, tag):
        if tag == 'stringtosign':
            self.active_tag = False

    def handle_data(self, data):
        if self.active_tag:
            self.data = data

    def get_bucket(self):
        if not self.data:
            return None

        data_tok = self.data.split("/")

        if len(data_tok)<2:
            return None

        return data_tok[1]


def get_bucket_name(domain):
    aws_key = aws_session.get_credentials().access_key
    url = 'https://%s/?AWSAccessKeyId=%s&Expires=1766972005&Signature=a' % (domain, aws_key)

    print("Trying:", url)
    r = requests.get(url)
    body = r.text

    if r.status_code != 403:
        print("Not a bucket, exiting")
        sys.exit(2)

    parser = StringToSignParser()
    parser.feed(body)
    parser.close()
    bucket_name = parser.get_bucket()

    return bucket_name


def check_bucket_permissions(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    print("Checking permissions on bucket", bucket_name)
    try:
        for bucket_obj in bucket.objects.all():
            print(" - Detected object:", bucket_obj.key)
        print(" *** Bucket is READABLE!:", bucket_name)
    except ClientError:
        print("not readable")

    try:
        bucket.put_object(Key='write-test.txt', Body='pwned!')
        bucket.delete_objects(Delete={'Objects': [{'Key': 'write-test.txt'}]})
    except ClientError:
        print("not writable")
        return

    print(" *** Bucket is WRITABLE!:", bucket_name)


def usage():
    print(USAGE_HELP % (sys.argv[0]))


def main():
    global aws_session

    try:
        aws_session = boto3.Session(profile_name='default')
    except botocore.exceptions.ProfileNotFound:
        print("Make sure AWS credentials are in ~/.aws")
        sys.exit(10)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:k:", [])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    domain = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o == "-d":
            domain = a
        else:
            assert False, "unhandled option"


    if not domain:
        print("No domain specified")
        sys.exit(4)

    try:
        bucket_name = get_bucket_name(domain)
        if not bucket_name:
            print("No bucket detected, exiting")
            sys.exit(1)

        print("Detected bucket:", bucket_name)
        check_bucket_permissions(bucket_name)
    except:
        print("Can't connect to domain", domain)


if __name__ == '__main__':
    main()
