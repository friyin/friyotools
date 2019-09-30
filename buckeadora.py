#!/usr/bin/env python3

import sys, requests, getopt, boto3, botocore
from html.parser import HTMLParser

from botocore.exceptions import ClientError

USAGE_HELP = """
Usage:
  %s -i domain_list_file | -d one_domain [-q]
  
Use - as file for stdin
"""

aws_key = None
aws_session = None

input_data = []

verbose_mode = False


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


def url_creator_from_input(domain_or_url_raw):
    domain_or_url= domain_or_url_raw.strip()
    detect_str = '?AWSAccessKeyId=%s&Expires=1766972005&Signature=a'
    if domain_or_url.startswith("http://") or domain_or_url.startswith("https://"):
        end_slash = '' if domain_or_url.endswith("/") else '/'
        return domain_or_url + end_slash + (detect_str % aws_key)

    return 'https://%s/?AWSAccessKeyId=%s&Expires=1766972005&Signature=a' % (domain_or_url, aws_key)


def get_bucket_name(url):

    if verbose_mode:
        print("Trying:", url)
    r = requests.get(url, timeout=5)
    body = r.text

    if r.status_code != 403:
        if verbose_mode:
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

    if verbose_mode:
        print("Checking permissions on bucket", bucket_name)
    try:
        for bucket_obj in bucket.objects.all():
            if verbose_mode:
                print(" - Detected object:", bucket_obj.key)
        print(" *** Bucket is READABLE!:", bucket_name)
    except ClientError:
        if verbose_mode:
            print("not readable")

    try:
        bucket.put_object(Key='write-test.txt', Body='pwned!')
        bucket.delete_objects(Delete={'Objects': [{'Key': 'write-test.txt'}]})
    except ClientError:
        if verbose_mode:
            print("not writable")
        return

    print(" *** Bucket is WRITABLE!:", bucket_name)


def read_domains_from_input(path):
    if path == "-":
        infile = sys.stdin
    else:
        infile = open(path, "r")

    result = infile.readlines()
    infile.close()
    return result


def usage():
    print(USAGE_HELP % (sys.argv[0]))


def process_data():
    for domain_or_url in input_data:
        try:
            url = url_creator_from_input(domain_or_url)
            bucket_name = get_bucket_name(url)
            if not bucket_name:
                if verbose_mode:
                    print("No bucket detected, exiting")
                sys.exit(1)

            if verbose_mode:
                print("Detected bucket:", bucket_name)
            check_bucket_permissions(bucket_name)
        except KeyboardInterrupt as ki:
            raise ki
        except:
            if verbose_mode:
                print("Can't connect to", domain_or_url)


def main():
    global aws_session, aws_key, input_data, verbose_mode

    try:
        aws_session = boto3.Session(profile_name='default')
        aws_key = aws_session.get_credentials().access_key
    except botocore.exceptions.ProfileNotFound:
        print("Make sure AWS credentials are in ~/.aws")
        sys.exit(10)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:i:v", [])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o == "-d":
            input_data = [a]
        elif o == "-i":
            input_data = read_domains_from_input(a)
        elif o == "-v":
            print("Verbose mode on")
            verbose_mode = True
        else:
            assert False, "unhandled option"

    if len(input_data) == 0:
        print("No domain specified")
        usage()
        sys.exit(4)

if __name__ == '__main__':
    main()
