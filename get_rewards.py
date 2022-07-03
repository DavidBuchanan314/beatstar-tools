import io
from datetime import datetime

from login import FlamingoSession, pprint
from gameconfig import GameConfig
import raksha
import protos

def timefmt(n):
	try:
		return datetime.utcfromtimestamp(n//1000).strftime('%Y-%m-%d %H:%M:%S')
	except ValueError:
		return "Forever"

def reward_to_string(config, rewards):
	strings = []
	for reward in rewards:
		rtype = reward["reward_type"]
		if rtype == 2 and reward["bar"]["foo"] == 3:
			strings.append(f'{reward["bar"]["gem_count"]} gems')
		elif rtype == 6:
			level_id = reward["bar"]["foo"]
			strings.append(f'Song: {config.level_names[level_id]}')
		elif rtype == 8:
			gacha_id = reward["bar"]["foo"]
			gachabox = config.gachaboxes[gacha_id]
			boxname = config.xlate[gachabox["name_xlate"]]
			cardtype = count = gachabox["contents"]["cards"][0]["cardtype"]
			count = gachabox["contents"]["cards"][0]["cardcount"]
			strings.append(f"{count}x {boxname} {config.cardtypes[cardtype]['id_name']}")
		elif rtype == 11:
			duration_ms = reward["bar"]["foo"]
			duration_mins = duration_ms/1000/60
			strings.append(f"unlimited play ({duration_mins} mins)")
		else:
			strings.append("UNKNOWN")
	return strings

if __name__ == "__main__":
	session = FlamingoSession()
	config_bin, version = session.get_resource("LiveOpsDeeplinkRewardConfig")
	config = GameConfig(session)

	print("Current version:", version)
	print()

	reward_config = raksha.parse_proto(io.BytesIO(config_bin), protos.rewards_proto)

	for reward in reward_config["rewards"]:
		start = reward.get("start", 0)
		end = reward.get("end", 0)

		print()
		print("Name:", reward["name"])
		print("Description:", ", ".join(reward_to_string(config, reward["rewards"]["rewards"])))
		print("Validity:", timefmt(start), timefmt(end))
		print("Deeplink:", "beatstar://?promo_id=" + reward["promo_id"])
		#pprint(reward)
