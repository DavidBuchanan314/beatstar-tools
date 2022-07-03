from gameconfig import GameConfig

config = GameConfig()

total = 0
for level_id, level in sorted(config.levels.items()):
	if "beatmap_id" not in level:
		continue
	beatmap = config.beatmaps[level["beatmap_id"]]
	track = config.tracks[level["track_id"]]

	if "MAYBE_IS_COMPLETE" not in beatmap:
		continue
	#if beatmap[12][1] != 5: # exclude tutorials
	#	continue
	if beatmap[4][1] != 3:
		continue

	print()
	print(f"{level_id}: {level['codename']}")

	difficulty = beatmap.get('difficulty', '???')
	print(f"\tBeatmap: {level['beatmap_id']}: {beatmap['idLabel']} - {difficulty}")

	print(f"\tSong: {level['track_id']}: {config.level_names[level_id]}  ({track.get('tstfile', '???')})")

	#print("legit" if beatmap.get("MAYBE_IS_JOURNEY", 0) else "leaked")
	#print(track)
	total += 1

print("total", total)
