from gameconfig import GameConfig

config = GameConfig()

journeys = {j["name"]: j for j in config.config["journey_variants"]}

for name in journeys.keys():
	print(name)

journey = journeys["gb"]
all_songs = set()
for level in journey["levels"]:
	print(level["level"])
	for song in level["songs"]:
		print("\t", config.level_names[song])
		all_songs.add(song)

for song in journey["event_songs"]:
	all_songs.add(song)

print("total:", len(all_songs))
