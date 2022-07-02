from gameconfig import GameConfig

config = GameConfig()

for level_id, level in sorted(config.levels.items()):
	if "beatmap_id" not in level:
		continue
	beatmap = config.beatmaps[level["beatmap_id"]]
	track = config.tracks[level["track_id"]]

	print()
	print(f"{level_id}: {level['codename']}")

	difficulty = beatmap.get('difficulty', '???')
	print(f"\tBeatmap: {level['beatmap_id']}: {beatmap['idLabel']} - {difficulty}")

	print(f"\tSong: {level['track_id']}: {config.level_names[level_id]}  ({track.get('tstfile', '???')})")
