import struct
from bitarray import bitarray
import socket

# message format
# 10101011  | 
# MI 8b 0:8 | origin ip 32b 8:40 | origin port 32b 40:72 | destiny ip 32b 72:104 | destiny port 32b 104:136 | type 4bits 136:140 | combination 4b 140:144 | bet 4b 144:148 | ph 1b 148: 

# Message types
# 1: message starting at the origin to choose who will roll the dice
# 2: message from origin to tell the player to make his play
# 3: message from player to the origin to update its balance
# 4: message from the origin to players updating balances
# 5: message to pass the bat -> is this a message? Does the bat has to be a struct?

class Message:
  __START_MARKER = '10101011'

  def __init__(self, message):
    self.binMessage = message
    self.message = message.decode()
    
    self.__validate()

    if(self.isGarbage()): 
      return

    self.bitMessage = bitarray(self.message)
    self.marker = self.bitMessage[0:8].to01()

    # sets origin related fields
    self.originIp = self.__decodeIp(self.bitMessage[8:40])
    self.originPort = self.__decodePort(self.bitMessage[40:72])

    # sets destiny related fields
    self.destinyIp = self.__decodeIp(self.bitMessage[72:104])
    self.destinyPort = self.__decodePort(self.bitMessage[104:136])

    # sets game related fields
    self.type = self.bitMessage[136:140].to01()
    self.combination = self.bitMessage[140:144].to01()
    self.bet = self.bitMessage[144:148].to01()
    self.ph = self.bitMessage[148:].to01()
    
  def print_me(self):
    print(self.marker)
    print(self.originIp)
    print(self.originPort)
    print(self.destinyIp)
    print(self.destinyPort)
    print(self.type)
    print(self.combination)
    print(self.bet)
    print(self.ph)

  def __validate(self):
    # If the message doesn't have the correct size, garbage is set to True.
    if(len(self.message) < 85):
      self.garbage = True
      return

    self.garbage = not self.message[0:8] == self.__START_MARKER

  def isGarbage(self):
    return self.garbage

  # receives a binary IP and returns as a string 
  @classmethod
  def __decodeIp(self, ip):
    return socket.inet_ntoa(int(ip.to01(), 2).to_bytes(4, 'big'))

  # receives an IP as a string and returns as a binary 
  @classmethod
  def __encodeIp(self, ip):
    return bin(struct.unpack('!I', socket.inet_aton(ip))[0])[2:].zfill(32).encode()

  # receives a port as a string and returns as a binary
  @classmethod
  def __encodePort(self, port):
    return bin(port)[2:].zfill(32).encode()

  # receives a binary port and returns as an integer
  @classmethod
  def __decodePort(self, port):
    return int(port.to01(), 2)

  @classmethod
  def binaryMessage(self, originIp, originPort, destinyIp, destinyPort, type, combination, bet):
    return self.__START_MARKER.encode() + self.__encodeIp(originIp) + self.__encodePort(originPort) + self.__encodeIp(destinyIp) + self.__encodePort(destinyPort) + type.encode() + combination.encode() + bet.encode() + b'1'

def main():
  binMessage = Message.binaryMessage(
    '127.0.0.1',
    5000,
    '127.0.0.1',
    5001,
    '0000',
    '1111',
    '0000'
  )

  msg = Message(binMessage)

  if(msg.isGarbage()):
    return

  msg.print_me()

if __name__ == '__main__':
  main()