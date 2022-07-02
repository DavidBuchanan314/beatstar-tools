import io

from login import FlamingoSession, pprint
import raksha
import protos
import translations

class GameConfig():
	def __init__(self, session=None):
		if session is None:
			session = FlamingoSession()
		self.session = session

		self.xlate = translations.get_english_translations(session)

		gameconf_bin, gameconf_version = session.get_resource("GameConfig")
		self.version = gameconf_version
		self.config = raksha.parse_proto(io.BytesIO(gameconf_bin), protos.gameconf_proto)

		# these map 1:1 to sound files
		self.tracks = {track['id']: track for track in self.config["track_infos"]}

		# these map 1:1 to beatmap files (e.g. a list of notes to tap)
		# they also have an associated track ID
		self.beatmaps = {beatmap['id']: beatmap for beatmap in self.config["beatmaps"]}

		# for lack of a better term, I'm calling these levels
		# a level is essentially a (track, beatmap) tuple
		self.levels = {level['id']: level for level in self.config["track_and_beatmap_pairs"]}

		# map levels to human-readable song names
		self.level_names = {
			level_id: " - ".join((
				self.xlate[self.tracks[level["track_id"]]["title"]],
				self.xlate[self.tracks[level["track_id"]]["artist"]]
			))
			for level_id, level in sorted(self.levels.items())
		}


if __name__ == "__main__":
	config = GameConfig()
	pprint(config.config)
