import io
from datetime import datetime

from login import FlamingoSession
import raksha
import protos

def timefmt(n):
	try:
		return datetime.utcfromtimestamp(n//1000).strftime('%Y-%m-%d %H:%M:%S')
	except ValueError:
		return "Forever"

session = FlamingoSession()
config_bin, version = session.get_resource("LiveOpsDeeplinkRewardConfig")

print("Current version:", version)
print()

config = raksha.parse_proto(io.BytesIO(config_bin), protos.rewards_proto)

for reward in config["rewards"]:
	start = reward.get("start", 0)
	end = reward.get("end", 0)

	print()
	print("Name:", reward["name"])
	print("Validity:", timefmt(start), timefmt(end))
	print("Deeplink:", "beatstar://?promo_id=" + reward["promo_id"])
