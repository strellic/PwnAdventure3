
import random

# +--first octet--+-second octet--+--third octet--+--fourth octet-+--fifth octet--+
# |7 6 5 4 3 2 1 0|7 6 5 4 3 2 1 0|7 6 5 4 3 2 1 0|7 6 5 4 3 2 1 0|7 6 5 4 3 2 1 0|
# +-----+---------+-+---------+---+-------+-------+-------------+-+---------+-----+
# |2 1 0|4 3 2 1 0|0|4 3 2 1 0|4 3|3 2 1 0|4 3 2 1|1 0|4 3 2 1 0|4|4 3 2 1 0|4 3 2|
# +2indx+-1.index-+4+-3.index-+-2-+5.index+4.index+-7-+-6.index-+5+-8.index-+7indx+

def base32encode(s, alphabet):

    encoded = ''
    bits = 0
    i = 0
    while bits < (len(s)*8):

        encoded += alphabet[(s[i] & 0b11111)]
        bits += 5
        if bits > (len(s)*8):
            break

        encoded += alphabet[((s[i+1] << 3) | (s[i] >> 5)) & 0b11111]
        bits += 5
        if bits > (len(s)*8):
            break

        encoded += alphabet[(s[i+1] >> 2) & 0b11111]
        bits += 5
        if bits > (len(s)*8):
            break

        encoded += alphabet[((s[i+2] << 1) | (s[i+1] >> 7)) & 0b11111]
        bits += 5
        if bits > (len(s)*8):
            break

        encoded += alphabet[((s[i+3] << 4) | (s[i+2] >> 4)) & 0b11111]
        bits += 5
        if bits > (len(s)*8):
            break

        encoded += alphabet[(s[i+3] >> 1) & 0b11111]
        bits += 5
        if bits > (len(s)*8):
            break

        encoded += alphabet[((s[i+4] << 2) | (s[i+3] >> 6)) & 0b11111]
        bits += 5
        if bits > (len(s)*8):
            break

        encoded += alphabet[(s[i+4] >> 3) & 0b11111]
        bits += 5
        if bits > (len(s)*8):
            break

        i += 5

    return encoded

def main():

    b32alphabet = '0123456789ABCDEFHJKLMNPQRTUVWXYZ'

    # PWNADV3 string - hard-coded part of DLC key
    PWNADV3 = bytearray([0x33, 0x56, 0x44, 0x41, 0x4E, 0x57, 0x50])

    # random part of DLC key
    rnd1 = random.randint(0,0x3FFFFFFF)
    #rnd1 = 0x44444400
    xored = (rnd1 ^ 0xAEB7037B) >> 2

    PWNADV3 += xored.to_bytes(4, byteorder='big')
    msg = int.from_bytes(PWNADV3, byteorder='big')

    rsa_encrypted = pow(msg, int("611C0519E05065E8F38DA1", 16), int("3C9921AC0185B3AAAE37E1B", 16))

    rnd1_bytes = rnd1.to_bytes(4, byteorder='little')
    buffer1 = bytearray(rsa_encrypted.to_bytes(12, byteorder='little'))
    buffer1[11] = buffer1[11] | int.from_bytes(rnd1_bytes[:1], byteorder='little')
    buffer1 += rnd1_bytes[1:]

    dlc_key = base32encode(buffer1, b32alphabet)

    check_sum = 0
    for char in dlc_key:
        check_sum += b32alphabet.find(char)

    dlc_key += b32alphabet[check_sum & 0b11111]

    #print(dlc_key)
    print(dlc_key[:5] + '-' + dlc_key[5:10] + '-' + dlc_key[10:15] + '-' + dlc_key[15:20] + '-' + dlc_key[20:25])

if __name__=='__main__':
    main()