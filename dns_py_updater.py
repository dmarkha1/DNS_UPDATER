import os
import json

import requests as req
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("TOKEN")
headers = {"Authorization": f"Bearer {token}"}

host = os.environ.get("HOST")


with open('my_domains.json') as f:
  domains_text = f.read()
  print(domains_text)
  domains = json.loads(domains_text)


# digital ocean documentation
# https://docs.digitalocean.com/reference/api/api-reference/#operation/domains_update_record

# https://api.ident.me/
dns_url = "https://ident.me/json"

do_base_url = f"https://api.digitalocean.com/v2/domains/{host}/records"

# Get current external IP info
curr_external_ip_data = req.get(dns_url).json()
curr_external_ip = curr_external_ip_data.get("ip")


if not os.path.exists("ip_data.json"):
    with open("ip_data.json", "w") as f:
        f.write(json.dumps(curr_external_ip_data))

with open("ip_data.json", "r") as f:
    old_external_ip_data = json.load(f)
    old_external_ip = old_external_ip_data.get("ip")
    #old_external_ip = "1.0.10.110" # for test


print(f"This is the current external ip: {curr_external_ip}")
print(f"This is the old external ip: {old_external_ip}")

if curr_external_ip == old_external_ip:
    print(f"\nCurrent IP ({curr_external_ip}) == Old IP ({old_external_ip}) --> do nothing.")
else:
    print(f"\nCurrent IP {curr_external_ip} != Old IP {old_external_ip} --> update file and DNS records")
    with open("ip_data.json", "w") as f:
        f.write(json.dumps(curr_external_ip_data))
        print("\tFile updated with new ip data: 'ip_data.json'\n")

    ## new digital ocean stuff goes here.
    for domain in domains:
        domain_url = f"{do_base_url}?name={domain}.{host}"
        # print(domain_url)
        do_domain_data = req.get(url=domain_url, headers=headers).json().get("domain_records")

        if len(do_domain_data):
            domain_id = do_domain_data[0].get("id")
            domain_name = do_domain_data[0].get("name")
            domain_curr_ip = do_domain_data[0].get("data")
            # print(do_domain_data)
            print(f"\tStarting update for domain '{domain_name}' ({domain_id})-> curr ip: {domain_curr_ip} to {curr_external_ip}")

            patch_data = json.dumps({"type":"A", "data": curr_external_ip})
            # print(patch_data)
            domain_update_url = f"{do_base_url}/{domain_id}"

            domain_update = req.put(url=domain_update_url, headers=headers, data=patch_data).json().get('domain_record')
            # print(domain_update)
            print(f"\tUpdated domain '{domain_name}' to {domain_update.get('data')}\n")




