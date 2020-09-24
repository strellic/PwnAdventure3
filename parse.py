import binascii
import struct

pos = None
slot = 1

def noop():
    global slot

    packet = bytearray(b's=\x00mvL\x90\x16\xc7O\xec\x99\xc6\xe0\xb5\x1cE\xb0\xf9\x0e\xa2\x00\x00\x00\x00')
    packet[2+0] = slot

    return packet

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = " ".join(map("{0:0>2X}".format, s))
        text = "".join([chr(x) if 0x20 <= x < 0x7F else "." for x in s])
        result.append("%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))
    return result

def h_position(data, queue, isLocal):
    global pos
    #if pos != data:
    #    print(struct.unpack("fff", data[2:2+4*3]))
    pos = data
    return pos

def h_switch(data, queue, isLocal):
    global slot

    if not isLocal:
        return data

    #print(f"slot = {data[2+0] + 1}")
    slot = data[2+0]

    return data

def h_jump(data, queue, isLocal):
    jumpActivated = data[2+0]
    #print(f"jump = {jumpActivated}")

    return data

def h_chat(data, queue, isLocal):
    global pos

    if not isLocal:
        return data

    length = struct.unpack("<H", data[2:2+2])[0]
    msg = data[2+2:2+2+length].decode()

    return data

def h_init(data, queue, isLocal):
    items = data.split(b"mk")

    for payload in items:
        if len(payload) < 2:
            continue

        id, _, _, _, _, length, _ = struct.unpack("HHHHBBB", payload[:11])
        name = payload[11:11+length]
        X,Y,Z = struct.unpack("fff", payload[11+length:11+length+(3*4)])
        print(f"[INIT] Actor #{id}: {name} @ {X} {Y} {Z}")

        if b"Drop" in name:
            pickup = struct.pack("=HI", 0x6565, actor_id)
            queue.server.append(pickup)

    return data

def h_inv_item(data, queue, isLocal):
    length = struct.unpack("H", data[2+0:2+2])[0]
    name = data[2+2:2+2+length]
    amount = struct.unpack("I", data[2+2+length:2+2+length+4])[0]
    print("new inv item: {}x {}".format(amount, name))
    return data

def h_pickup_drop(data, queue, isLocal):
    drop_id = struct.unpack("I", data[2+0:2+4])[0]
    print("pickup drop: ID {:x}".format(drop_id))
    return data[4:]

def h_health(data, queue, isLocal):
    id, hp = struct.unpack("Ii", data[2+0:2+8])
    #print(f"health: {id}: {hp} HP")
    return data

def h_circuit(data, queue, isLocal):
    length = struct.unpack("H", data[2+0:2+2])[0]
    name = data[2+2:2+2+length]

    inputs = struct.unpack("I", data[2+2+length:2+2+length+4])[0]
    inbits = bin(inputs)[2:].zfill(32)

    if not isLocal and name == b"FinalStage":
        out = int(data[2+2+length+4+2:2+2+length+4+2+22].hex(), 16)
        bits = bin(out)[2:].zfill(176)

        check = "".join([bits[x] for x in [14, 96, 119, 123, 128, 136, 140, 145, 148, 154, 158, 160, 163, 167, 173]])
        if check == '000000000000000':
            print(f"open! correct bits: {inbits}")
            print(f"open! correct bits: {inbits}")
            print(f"open! correct bits: {inbits}")
            print(f"open! correct bits: {inbits}")
            print(f"open! correct bits: {inbits}")
            print(f"open! correct bits: {inbits}")
            queue.server = []
        else:
            pass

    return data

def h_noop(data, queue, isLocal):
    return data

handlers = {
    "6d76": h_position,
    "0000": h_noop,
    "733d": h_switch,
    "6a70": h_jump,
    "232a": h_chat,
    "6d6b": h_init,
    "2b2b": h_health,
    "3031": h_circuit,
    #"7073": h_noop, # monsters
    #"6d61": h_noop, # mana
    #"6672": h_noop, # static link
    #"2a69": h_noop, # weapon shoot
    #"7878": h_noop, # remove
    #"7374": h_noop, # ???
    #"6370": h_inv_item,
    #"6565": h_pickup_drop,
}

def banner(msg_top, msg_bottom):
    return b"ev" + struct.pack("H", len(msg_top)) + msg_top.encode() + struct.pack("H", len(msg_bottom)) + msg_bottom.encode()

def parse(data, connection, queue, isLocal):
    if connection[1] == 3333:
        return data

    data = bytearray(data)

    tag = "L -> " if isLocal else "R <- "

    #print(f"[{tag}{connection[1]}] {len(data)} bytes intercepted: {data}")

    if len(data):
        hData = binascii.hexlify(data).decode()
        data = handlers.get(hData[:4], h_noop)(data, queue, isLocal)

        '''
        if hData[:4] not in handlers:
            print(f"[{tag}{connection[1]}] Unknown {len(data)} bytes intercepted: {data}")
            dump = hexdump(data)
            for line in dump:
                print(f"\t{line}")
        '''

    return data

def cmd_parse(cmd, hook):
    return False

class Utils():
    def __init__(self, queue, parse, fridahook):
        self.queue = queue
        self.parse = parse
        self.fridahook = fridahook

    def banner(self, top, bot):
        self.queue.client.append(self.parse.banner(top, bot))

    def circuit(self, bits):
        data = int(bits, 2)
        self.queue.server.append(binascii.unhexlify("30310a0046696e616c5374616765") + struct.pack("<I", data))