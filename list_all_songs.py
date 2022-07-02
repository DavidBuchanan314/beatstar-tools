import io

from login import FlamingoSession
import raksha
import protos
import translations

session = FlamingoSession()

english_translations = translations.get_english_translations(session)

gameconf_bin, gameconf_version = session.get_resource("GameConfig")
game_config = raksha.parse_proto(io.BytesIO(gameconf_bin), protos.gameconf_proto)

tracks = {track['id']: track for track in game_config["track_infos"]}


# print tracks by id
"""
for track_id in sorted(tracks.keys()):
	track = tracks[track_id]
	artist = english_translations[track["artist"]]
	title = english_translations[track["title"]]
	print(f"{track_id}: {title} - {artist}  ({track.get('tstfile', '???')})")
	#pprint(track)
"""

beatmaps = {beatmap['id']: beatmap for beatmap in game_config["beatmaps"]}

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
