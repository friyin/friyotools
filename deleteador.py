import subprocess
import json
import sys

if len(sys.argv) !=4:
    print(f"Usage {sys.argv[0]} domain accessKey secretKey")
    sys.exit(1)

domain = sys.argv[1]
accessKey = sys.argv[2]
secretKey = sys.argv[3]

command = "AWS_ACCESS_KEY_ID=" + accessKey + " AWS_SECRET_ACCESS_KEY=" + secretKey + " aws route53 list-hosted-zones"
out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
stdout, stderr = out.communicate()
json_data = None


if stdout != 'false':
    json_data = json.loads(stdout)

zones_to_be_removed = []

print("Domain to delete: " + domain)

for zone in json_data["HostedZones"]:
    if domain.lower().strip(".") == str(zone["Name"]).lower().strip("."):
        zones_to_be_removed.append(str(zone["Id"].replace("/hostedzone/", "")))

print("zones_to_be_removed: "+str(zones_to_be_removed))
print(f"# zones to be removed for domain {domain}: {len(zones_to_be_removed)}")

if len(zones_to_be_removed) == 0:
    print("There are no zones to delete, exiting")
    sys.exit(1)

confirm = input("Are you sure?: ")
if confirm != 'y':
    print("Cancelled!")
    sys.exit(1)

for zone in zones_to_be_removed:
    print("Removing: "+zone)

    command = "AWS_ACCESS_KEY_ID=" + accessKey + " AWS_SECRET_ACCESS_KEY=" + secretKey + " aws route53 delete-hosted-zone --id " + str(
        zone)
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = out.communicate()
