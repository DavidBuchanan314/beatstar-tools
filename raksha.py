import io
import struct

"""
Raksha is a variant of protobuf that allows repeated messages.
I couldn't get it to parse with existing protobuf tools, so I had to make
my own.
"""

# TYPES

class String():
	def __init__(self):
		pass

class Bytes():
	def __init__(self):
		pass

class Varint():
	def __init__(self):
		pass

class Float():
	def __init__(self):
		pass

class U32():
	def __init__(self):
		pass

class Packed():
	def __init__(self, proto):
		self.proto = proto

# PARSING

def parse_varint(stream):
	n = 0
	ctr = 0
	while True:
		foo = stream.read(1)
		if not foo:
			return None
		x = foo[0]
		n |= (x & 0x7f) << (7*ctr)
		if not x & 0x80:
			return n
		ctr += 1

def get_field_and_type(varint):
	field = varint >> 3
	wire_type = varint & 7
	return field, wire_type

def parse_unknown_type(stream, wire_type=None):
	if wire_type is None:
		tag = parse_varint(stream)
		if tag is None:
			return None
		field, wire_type = get_field_and_type(tag)
	#print("field", field, wire_type)
	if wire_type == 0:
		return ("varint", parse_varint(stream))
	elif wire_type == 2:
		length = parse_varint(stream)
		#print(length)
		body = stream.read(length)
		return ("length-delimited", body)
	elif wire_type == 5:
		return ("fixed32", stream.read(4).hex())
	else:
		raise Exception("unknown wire type", wire_type)

def parse_unknown_message(stream):
	entries = []
	while True:
		thing = parse_unknown_type(stream)
		if thing is None:
			return entries
		entries.append(thing)

def parse_unknown_repeated(stream):
	chunks = []
	while True:
		length = parse_varint(stream)
		if length is None:
			return chunks
		body = stream.read(length)
		chunks.append(parse_unknown_message(io.BytesIO(body)))

def parse_proto(stream, proto={}, wire_type=None, top_level=True):
	if type(proto) is dict:
		if wire_type is not None:
			assert(wire_type == 2)
		if not top_level:
			length = parse_varint(stream)
			if length is None:
				return None
			substream_bytes = stream.read(length)
			assert(len(substream_bytes) == length)
			stream = io.BytesIO(substream_bytes)
		fields = {}
		while True:
			tag = parse_varint(stream)
			if tag is None:
				break
			field, wire_type = get_field_and_type(tag)
			field_name, field_proto = proto.get(field, (field, None))
			value = parse_proto(stream, field_proto, wire_type=wire_type, top_level=False)
			if value is None:
				break
			if field_name in fields:
				if type(fields[field_name]) is list:
					fields[field_name].append(value)
				else:
					# TODO: exception if not repeated type?
					fields[field_name] = [fields[field_name], value]
			else:
				fields[field_name] = value
		return fields
	elif type(proto) is String:
		if wire_type is not None:
			assert(wire_type == 2)
		length = parse_varint(stream)
		if length is None:
			return None
		string = stream.read(length)
		assert(len(string) == length)
		return string.decode()
	elif type(proto) is Bytes:
		if wire_type is not None:
			assert(wire_type == 2)
		length = parse_varint(stream)
		if length is None:
			return None
		string = stream.read(length)
		assert(len(string) == length)
		return string
	elif type(proto) is Varint:
		if wire_type is not None:
			assert(wire_type == 0)
		return parse_varint(stream)
	elif type(proto) is Float:
		if wire_type is not None:
			assert(wire_type == 5)
		return struct.unpack("<f", stream.read(4))[0]
	elif type(proto) is Packed:
		if wire_type is not None:
			assert(wire_type == 2)
		length = parse_varint(stream)
		if length is None:
			return None
		substream_bytes = stream.read(length)
		assert(len(substream_bytes) == length)
		substream = io.BytesIO(substream_bytes)
		#return parse_unknown_repeated(substream)
		messages = []
		while True:
			"""
			subsubstream_len = parse_varint(substream)
			if subsubstream_len is None:
				break
			subsubstream_bytes = substream.read(subsubstream_len)
			assert(len(subsubstream_bytes) == subsubstream_len)
			subsubstream = io.BytesIO(subsubstream_bytes)
			msg = parse_proto(subsubstream, proto.proto)
			"""
			msg = parse_proto(substream, proto.proto, top_level=False)
			#msg = parse_unknown_message(subsubstream)
			if msg is None:
				break
			messages.append(msg)
		return messages
	elif proto is None:
		return parse_unknown_type(stream, wire_type=wire_type)
	
	raise Exception("unnknown proto:", proto)




# SERIALISING

def serialize_varint(stream, n):
	while n > 0x7f:
		stream.write(bytes([0x80 | (n & 0x7f)]))
		n >>= 7
	stream.write(bytes([n]))

def serialize_field_and_type(stream, field, type):
	serialize_varint(stream, (field << 3) | type)

def serialize_proto(stream, data, proto={}, field=None, top_level=True):
	if type(proto) is Packed:
		assert(type(data) is list)
		substream = io.BytesIO()
		for msg in data:
			subsubstream = io.BytesIO()
			serialize_proto(subsubstream, msg, proto.proto, top_level=False)
			subsubstream_bytes = subsubstream.getvalue()
			#serialize_varint(substream, len(subsubstream_bytes))
			substream.write(subsubstream_bytes)
		substream_bytes = substream.getvalue()
		serialize_field_and_type(stream, field, 2)
		serialize_varint(stream, len(substream_bytes))
		stream.write(substream_bytes)
		return
	# TODO: if data is array, iterate through and recurse, return
	if type(data) is list:
		for datum in data:
			serialize_proto(stream, datum, proto=proto, field=field, top_level=False)
		return
	# else
	if type(proto) is dict:
		substream = io.BytesIO()
		for key in data.keys():
			field_number = ([k for k in proto.keys() if proto[k][0] == key]+[key])[0]
			field_proto = None if field_number is None else (proto[field_number][1] if field_number in proto else None)
			serialize_proto(substream, data[key], field_proto, field=field_number, top_level=False)
		substream_bytes = substream.getvalue()
		if field is not None:
			serialize_field_and_type(stream, field, 2)
		if not top_level:
			serialize_varint(stream, len(substream_bytes))
		stream.write(substream_bytes)
	elif type(proto) is Varint:
		assert(type(data) is int)
		if field is not None:
			serialize_field_and_type(stream, field, 0)
		serialize_varint(stream, data)
	elif type(proto) is String:
		assert(type(data) is str)
		serialize_field_and_type(stream, field, 2)
		str_bytes = data.encode()
		serialize_varint(stream, len(str_bytes))
		stream.write(str_bytes)
	elif type(proto) is Bytes:
		assert(type(data) is bytes)
		serialize_field_and_type(stream, field, 2)
		serialize_varint(stream, len(data))
		stream.write(data)
	elif type(proto) is U32:
		assert(type(data) is int)
		serialize_field_and_type(stream, field, 5)
		stream.write(data.to_bytes(4, "little"))

	elif proto is None: # time to guess
		if type(data) is tuple and len(data) == 2:
			if data[0] == "length-delimited":
				serialize_proto(stream, data[1], proto=Bytes(), field=field)
				return
			if data[0] == "fixed32":
				serialize_proto(stream, int.from_bytes(bytes.fromhex(data[1]), "little"), proto=U32(), field=field)
				return
			if data[0] == "varint":
				serialize_proto(stream, data[1], proto=Varint(), field=field)
				return
		raise Exception(f"blah: {data}")
	else:
		raise Exception("unknown proto", proto)
		# TODO: guess based on type of data

if __name__ == "__main__":
	my_proto = {
		1: ("foo", Varint()),
		2: ("bar", String()),
		3: ("bat", Packed({
			7: ("blah", String())
		})),
		4: ("msg", {
			123: ("456", Varint())
		})
	}

	my_obj = {
		"foo": 1234,
		"bar": "hello",
		"bat": [{
			"blah": "blah"
		},{
			"blah": "banana"
		}],
		"msg": {
			"456": 789
		}
	}

	buf = io.BytesIO()
	serialize_proto(buf, my_obj, my_proto)
	print(buf.getvalue())
	print(parse_proto(io.BytesIO(buf.getvalue()), my_proto))
