from raksha import String, Varint, PackedMessage, Float

# login stuff

request_header_proto = {
	1: ("version", String()),
	2: ("service", String()),
	3: ("rpcthing", String()),
	4: ("authenticationTicket", String()),
	6: ("unk0", Varint()),
	7: ("unk1", Varint()),
	9: ("clide", String())
}

response_header_proto = {
	1: ("dunno", String()),
	2: ("timestamp", Varint()),
	3: ("rpcthing", String()),
	7: ("gzipped", Varint())
}

# com.spaceape.rpc.userservice.BaseReq
userservice_basereq_proto = {
	1: ("id", Varint()),
	2: ("type", Varint()), # Login=2, AllInOneLogin=7, GetIdentity=210
	7: ("appVersion", String()),
	11: ("timestamp", Varint()),
	112: ("all_in_one_login", {
		3: ("cinta", String()), # a UUID
		15: ("???", Varint())
	})
}

server_hello_proto = {
	4: ("upgrade_info", {
		1: ("upgrade_version", String()),
		2: ("apple", String()),
		3: ("android", String())
	}),
	112: ("blah", {})
}

# come.spaceape.rpc.userservice.BaseResp
userservice_baseresp_proto = {
	1: ("id", Varint()),
	2: ("type", Varint()),
	3: ("status", Varint()),
	112: ("resp_login_of_some_type", {
		1: ("authenticationTicket", String()),
		2: ("clide", String()), # dunno what this is short for, but it's a UUID
		3: ("expiryTime", Varint()),
		4: ("cinta", String()), # dunno what this is short for, but it's a UUID
	})
}

cmsreq_proto = {
	1: ("id", Varint()), # probably id
	2: ("version", String()),
	3: ("timestamp", Varint()),
	4: ("unk1", String()), # an empty string?
	5: ("versions", {
		1: ("unk0", Varint()),
		2: ("unk1", String()),
		3: ("unk2", Varint()),
		4: ("vers", {
			1: ("versionlist", {
				1: ("name", String()),
				2: ("localVersion", String()),
				3: ("localHash", String()),
				7: ("locale", String())
			})
		})
	}),
	6: ("authenticationTicket", String())
}

cms_res_proto = {
	1: ("probably_id", Varint()),
	2: ("timestamp", Varint()),
	5: ("blah", {
		5: ("blah", {
			1: ("blah", {
				1: ("name", String()),
				2: ("version", String()),
				3: ("hash", String()),
				5: ("url", String())
			}),
			2: ("something", {})
		})
	})
}

rewards_proto = {
	100: ("version", String()),
	1: ("rewards", PackedMessage({
		1: ("promo_id", String()),
		2: ("name", String()),
		3: ("unk0", Varint()),
		5: ("start", Varint()),
		6: ("end", Varint()),
		7: ("rewards", {
			1: ("rewards", PackedMessage({
				1: ("reward_type", Varint()), # 11=unlimited_play, 8=cards, 2=gems, 6=song
				2: ("bar", {
					1: ("foo", Varint()), # enum gems=3, unlimited_play=1800000, 2hardcards=117, alternativecards=154, popcards=153, rockcards=151, wishlist10=608, rainbow2=610
					2: ("gem_count", Varint()),
				})
			}))
		}),
		8: ("url", String())
	})),
}

assetpatch_proto = {
	1: ("version", String()),
	6: ("url_base", String()),
	7: ("subdir", String()),
	4: ("assets", PackedMessage({
		1: ("name", String()),
		5: ("hash", String()),
		6: ("length", Varint()),
		7: ("crc32", Varint()),
		8: ("old_hash", String()), # maybe???
		9: ("old_length", Varint()),
		10: ("old_crc32", Varint()),
	}))
}

gameconf_proto = {
	1000: ("version", String()),
	3: ("track_and_beatmap_pairs", { # seems to join audio files and beatmaps
		1: ("id", Varint()),
		21: ("track_id", Varint()), # matches id used in track_infos list 
		37: ("codename", String()), # vaguely human readable descriptor
		46: ("beatmap_id", Varint()) # matches beatmap filename
	}),
	25: ("track_infos", {
		1: ("id", Varint()),
		19: ("hash", String()),
		66: ("tstfile", String()),
		76: ("title", String()),
		77: ("artist", String()),
	}),
	102: ("categories", PackedMessage({})),
	105: ("artists", PackedMessage({
		1: ("artist_id", Varint()),
		2: ("artist_name", String()),
		3: ("artist_name_short", String()),
	})),
	#107: ("emojis", PackedMessage({})),
	#109: ("effects", PackedMessage({})),
	#110: ("tags", PackedMessage({})),
	119: ("gachaboxes", PackedMessage({
		1: ("id", Varint()),
		2: ("id_name", String()),
		28: ("unk0", PackedMessage({
			1: ("???", {
				2: ("???", PackedMessage({
					2: ("???", {})
				}))
			}),
		})),
		33: ("contents", {
			2: ("cards", PackedMessage({
				1: ("cardtype", Varint()),
				2: ("cardcount", Varint()),
			}))
		}),
		37: ("name_xlate", String()),
	})),
	144: ("cardtypes", PackedMessage({
		1: ("id", Varint()),
		2: ("id_name", String()),
		11: ("???", {})
	})),
	145: ("cardboxes", PackedMessage({})), # has info about how many you need to unlock the next song from that box, display names
	146: ("cardfoo",  PackedMessage({})),
	148: ("beatmaps", {
		1: ("id", Varint()), # maps to the number in beatmap file name, and id in headers
		2: ("idLabel", String()), # matches those in beatmap file headers
		3: ("track_id", Varint()), # seems to be the first number in the above?
		5: ("unk0", Varint()), # perhaps something to do with score normalisation? the max score maybe? It's always a multiple of 50!
		13: ("hash", String()), # not sure what this is *exactly*
		15: ("difficulty", String())
	}),
	174: ("songboxes", PackedMessage({
		1: ("id", Varint()),
		2: ("name", String()),
		3: ("info", {
			13: ("foo", {
				2: ("bar", {})
			})
		})
	})),
	177: ("shopitems", PackedMessage({

	})),
	1017: ("loadingtips", {
		2: ("tips", String())
	}),
}

langconf_proto = {
	1: ("translations", {
		1: ("key", String()),
		2: ("values", {
			1: ("locale", String()),
			2: ("translation", String())
		})
	}),
	2: ("languages", {

	}),
	100: ("version", String())
}

interaction_position_proto = {
	1: ("pos", Float()),
	2: ("range", {
		1: ("top", Float()),
		2: ("bottom", Float())
	})
}

beatmap_proto = {
	1: ("id", Varint()),
	2: ("idLabel", String()),
	5: ("interactionData", PackedMessage({
		1: ("interactionType", Varint()),
		3: ("tapInteractionData", {
			1: ("position", interaction_position_proto)
		}),
		4: ("dragInteractionData", {
			1: ("position", interaction_position_proto)
		}),
		6: ("track", Varint()), # looks like this defaults to 1 if not present
		13: ("MYSTERY", Varint()),
	})),
	6: ("sections", PackedMessage({
		1: ("f", Float()),
	})),
	7: ("blah2", PackedMessage({
		1: ("f0", Float()),
		2: ("f1", Float()),
	})),
	8: ("blah3", PackedMessage({
		1: ("f0", Float()),
		2: ("f1", Float()),
	})),
	9: ("blah4", PackedMessage({
		1: ("f", Float()),
	})),
}
