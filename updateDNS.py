from requests import *
import json
import time

with open("config.json") as f:
	config = json.load(f)
apikey = config["apikey"]
email = config["email"]
print("Starting updater")


header = {"Content-Type": "application/json", "X-Auth-Key": apikey, "X-Auth-Email": email}
r = get("https://api.cloudflare.com/client/v4/zones", headers=header)
if r.raise_for_status():
	print("Error")
r = r.json()
if r["success"]:
	id = r["result"][0]["id"]
	zones = get("https://api.cloudflare.com/client/v4/zones/" + id + "/dns_records", headers=header).json()["result"]
	zone_ids = []
	for i in range(len(zones)):
		if zones[i]["type"] == "A":
			zone_ids.append(zones[i]["id"])
	while True:
		cf_ip = zones[0]["content"]
		# get current IP address
		ip = get("https://api.ipify.org").text
		if cf_ip == ip:
			# IP didn't change -> wait until next check
			time.sleep(900)
		else:
			for zone_id in zone_ids:
				# Update records

				r = patch("https://api.cloudflare.com/client/v4/zones/" + id + "/dns_records/" + zone_id, json.dumps({"content": ip}), headers=header)
				print("Updated record for " + zone_id)
				time.sleep(900)
else:
	print("Error. Wrong credentials?")
	print(r)
