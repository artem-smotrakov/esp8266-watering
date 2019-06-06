try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

from socket import AF_INET, SOCK_DGRAM

NTP_PACKET_FORMAT = '!12I'
NTP_DELTA = 2208988800 # 1970-01-01 00:00:00
NTP_QUERY = b'\x1b' + 47 * b'\0'

def time(host="pool.ntp.org", port=123):
    with socket.socket(AF_INET, SOCK_DGRAM) as s:
        s.sendto(NTP_QUERY, (host, port))
        msg, address = s.recvfrom(1024)
        unpacked = struct.unpack(NTP_PACKET_FORMAT,
                                 msg[0:struct.calcsize(NTP_PACKET_FORMAT)])
        return int(unpacked[10] + unpacked[11] / 2**32 - NTP_DELTA)
