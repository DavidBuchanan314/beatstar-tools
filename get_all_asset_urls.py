import io

from login import FlamingoSession
import raksha
import protos

session = FlamingoSession()
config_bin, version = session.get_resource("AssetsPatchConfig")

print("Current version:", version)
print()

config = raksha.parse_proto(io.BytesIO(config_bin), protos.assetpatch_proto)

for asset in config["assets"]:
	url = f'{config["url_base"]}/{config["subdir"]}/Android/{asset["name"]}_{asset["hash"]}{asset["crc32"]}.bundle'
	print(url)
