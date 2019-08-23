#!/usr/bin/env python3

import sqlite3, getopt, sys, datetime, subprocess
conn = None
domains = None
#verbose = False

STATUS_OPEN = 0
STATUS_CLOSED = 1
STATUS_FILTERED = 2

USAGE_HELP = """
Usage:
  %s -i domains.txt
    or
  cat domains.txt | %s -i -
"""


def open_db(path='domains.db'):
    global conn
    conn = sqlite3.connect(path)


def close_db():
    conn.close()


def exec_q(query, commit=True):
    c = conn.cursor()
    c.execute('''CREATE TABLE domain (domain text, date date)''')
    if commit:
        conn.commit()


def init_db():
    c = conn.cursor()
    # Create table
    c.execute('CREATE TABLE IF NOT EXISTS domain ('
              'domain text, '
              'date date, '
              'PRIMARY KEY(domain))')
    c.execute('CREATE TABLE IF NOT EXISTS port ('
              'domain TEXT, '
              'port INTEGER, '
              'status INTEGER, '
              'PRIMARY KEY (domain,port), '
              'FOREIGN KEY(domain) REFERENCES domain(domain))')

    conn.commit()

def populate_db():
    c = conn.cursor()

    c.execute("INSERT INTO domain VALUES ('google.com', '2010-08-23')")
    c.execute("INSERT INTO domain VALUES ('yahoo.com', '2010-08-22')")

    c.execute("INSERT INTO port VALUES ('google.com', 80, 0)")
    c.execute("INSERT INTO port VALUES ('google.com', 443, 0)")
    c.execute("INSERT INTO port VALUES ('google.com', 8080, 1)")

    c.execute("INSERT INTO port VALUES ('yahoo.com', 80, 0)")
    c.execute("INSERT INTO port VALUES ('yahoo.com', 443, 0)")
    c.execute("INSERT INTO port VALUES ('yahoo.com', 9090, 0)")
    c.execute("INSERT INTO port VALUES ('yahoo.com', 8443, 2)")

    conn.commit()


def fetch_domains():
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    c.execute("SELECT domain FROM domain")
    return set(c.fetchall())


def after_sub(str, sub):
    i = str.find(sub)

    if i > -1:
        return str[str.find(sub) + 1:]

    return str


def before_sub(str, sub):
    i = str.find(sub)

    if i > -1:
        return str[:str.find(sub)]

    return str


def filter_domain(domain):
    domain = domain.strip()
    domain = after_sub(domain, "//")
    domain = after_sub(domain, "/")
    domain = after_sub(domain, "*.")
    domain = after_sub(domain, "*")
    domain = before_sub(domain, "/")
    if domain.startswith('.'):
        domain = domain[1:]

    if domain.find('.') == -1:
        return None

    return domain


def add_domains(new_domains):
    today = datetime.date.today()

    c = conn.cursor()
    for domain in new_domains:
        print("%s" % domain)
        c.executemany("INSERT INTO domain (domain, date) VALUES (?, ?)", [(domain, today)])
    conn.commit()


def list_domains():
    print("%d domain(s) found" % len(domains))
    print()
    for domain in domains:
        print("%s" % domain)


def scan_domain(domain):
    subprocess.Popen(["nmap", "-P0", "-F",domain])


def handle_input(path):
    if path == "-":
        infile = sys.stdin
    else:
        infile = open(path, "r")

    in_domains = infile.readlines()
    infile.close()

    filtered_domains = [filter_domain(x) for x in in_domains]

    received_domains = set(filtered_domains)

    to_add_domains = received_domains.difference(domains)
    to_add_domains.remove(None)

    print("Detected %d new domain(s) to add" % len(to_add_domains))

    add_domains(to_add_domains)


def usage():
    print(USAGE_HELP % (sys.argv[0], sys.argv[0]))


def main():
    global domains, verbose

    open_db()
    init_db()
    domains = fetch_domains()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:vl", ["help", "input=", "list"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o in ("-i", "--input"):
            handle_input(a)
        elif o in ("-l", "--list"):
            list_domains()
        else:
            assert False, "unhandled option"


if __name__ == "__main__":
    main()
