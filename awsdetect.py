#!/usr/bin/env python

import sys
import dns.resolver
import whois
import time

exceptions_tuple = (
    dns.resolver.NoAnswer,
#    dns.resolver.NXDOMAIN,
#    dns.resolver.NoNameservers,
    dns.name.EmptyLabel,
    dns.exception.Timeout,
    AttributeError,
    whois.exceptions.UnknownTld,
    whois.exceptions.FailedParsingWhoisOutput,
    KeyError)

def is_dom(victimDomain):
    try:
        dns.resolver.query(victimDomain, 'A')
        return False
#    except dns.resolver.NoAnswer:
#        return True
    except dns.resolver.NoNameservers:
        return True
    except dns.resolver.NXDOMAIN:
        return True
    except exceptions_tuple:
        return False

def get_ns(victimDomain):
    try:
        return list(whois.query(victimDomain).name_servers)
    except exceptions_tuple:
        pass

    try:
        return dns.resolver.query(victimDomain, 'NS')
#    except dns.resolver.NoAnswer:
#        pass
    except dns.resolver.NoNameservers:
        pass
    except dns.resolver.NXDOMAIN:
        pass
    except exceptions_tuple:
        pass

    return None

def has_aws(domains):
    for domain in domains:
        if "awsdns-" in str(domain):
            return True

    return False


with open(sys.argv[1], 'r') as f:
    domains = f.readlines()


domains_set = set(['.'.join(x.strip().split('.')[-2:]) for x in domains])


for domain in domains_set:
    print("Domain: "+domain, file=sys.stderr)

    if is_dom(domain):
        time.sleep(2)
        print(" - Domain unresolvable, triying aws:", domain, file=sys.stderr)

        for i in range(0, 2):
            try:
                ns = get_ns(domain)
                if ns and has_aws(ns):
                    print("VULNERABLE: "+domain, file=sys.stderr)
                    print(domain)

                break
            except whois.exceptions.WhoisCommandFailed as e:
                print(f"WHOIS Command failed: {e}, sleeping 300", file=sys.stderr)
                time.sleep(300)


