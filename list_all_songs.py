import io

from login import FlamingoSession, pprint
import raksha
import protos
import translations

session = FlamingoSession()

english_translations = translations.get_english_translations(session)

gameconf_bin, gameconf_version = session.get_resource("GameConfig")
game_config = raksha.parse_proto(io.BytesIO(gameconf_bin), protos.gameconf_proto)

#pprint(game_config)
#exit()

# these map 1:1 to sound files
tracks = {track['id']: track for track in game_config["track_infos"]}

# these map 1:1 to beatmap files (e.g. a list of notes to tap)
# they also have an associated track ID
beatmaps = {beatmap['id']: beatmap for beatmap in game_config["beatmaps"]}

# for lack of a better term, I'm calling these levels
# a level is essentially a (track, beatmap) tuple
levels = {level['id']: level for level in game_config["track_and_beatmap_pairs"]}


# print tracks by id
"""
for track_id in sorted(tracks.keys()):
	track = tracks[track_id]
	artist = english_translations[track["artist"]]
	title = english_translations[track["title"]]
	print(f"{track_id}: {title} - {artist}  ({track.get('tstfile', '???')})")
	#pprint(track)
"""

# print beatmaps by id
"""
for beatmap_id in sorted(beatmaps.keys()):
	beatmap = beatmaps[beatmap_id]
	print()
	#print(beatmap)

	difficulty = beatmap.get('difficulty', '???')
	#if difficulty not in ["Normal", "Hard", "Extreme"]:
	#	continue
	print(f"{beatmap_id}: {beatmap['idLabel']} - {difficulty}")
	#print(beatmap.get("unk0", "???"))

	track = tracks[beatmap["track_id"]]
	artist = english_translations[track["artist"]]
	title = english_translations[track["title"]]
	print(f"\tSong: {beatmap['track_id']}: {title} - {artist}  ({track.get('tstfile', '???')})")
"""

for level_id in sorted(levels.keys()):
	level = levels[level_id]
	if "beatmap_id" not in level:
		continue
	beatmap = beatmaps[level["beatmap_id"]]
	track = tracks[level["track_id"]]

	print()
	print(f"{level_id}: {level['codename']}")

	difficulty = beatmap.get('difficulty', '???')
	print(f"\tBeatmap: {level['beatmap_id']}: {beatmap['idLabel']} - {difficulty}")

	artist = english_translations[track["artist"]]
	title = english_translations[track["title"]]
	print(f"\tSong: {level['track_id']}: {title} - {artist}  ({track.get('tstfile', '???')})")
