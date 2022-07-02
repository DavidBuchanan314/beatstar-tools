import io

import raksha
import protos

def get_english_translations(flamingo_session):
	langconf_bin, langconf_version = flamingo_session.get_resource("LangConfig")
	lang_config = raksha.parse_proto(io.BytesIO(langconf_bin), protos.langconf_proto)

	english_translations = {}
	for translation in lang_config["translations"]:
		if "values" not in translation:
			continue
		values = translation["values"]
		if type(values) is not list:
			values = [values]
		value = [x["translation"] for x in values if x["locale"] == "en"][0]
		english_translations[translation["key"]] = value
	
	return english_translations
