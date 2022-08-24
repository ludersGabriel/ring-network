from random import randrange
import string
import struct
from bitarray import bitarray
import socket

# message format
# 10101011  | 
# MI 8b 0:8 | player ip 32b 8:40 | player port 32b 40:72 | type 4bits 72:76 | combination 4b 76:80 | bet 4bytes 80:112 | ph 1b 112:  
# b = bits

class Message:
  __START_MARKER = '10101011'

  # message types
  _BETTING = '0001'
  _CHOSEN_PLAYER = '0010'
  _UPDATE_PLAYER_BALANCE = '0011'
  _PASSING_BAT = '0100'
  _GREETING = '0101'
  _RESULT = '0110'
  _END_GAME = '0111'
  _ERROR = '1000'

  def __init__(self, message):
    assert isinstance(message, bytes)
    
    self.binMessage = message
    self.message = message.decode()
    
    self.__validate()

    self.bitMessage = bitarray(self.message)
    self.marker = self.bitMessage[0:8].to01()

    # sets current player fields
    self.playerIp = self.__decodeIp(self.bitMessage[8:40])
    self.playerPort = self.__decodePort(self.bitMessage[40:72])
    self.playerId = f'{self.playerIp}:{self.playerPort}'

    # sets game related fields
    self.type = self.bitMessage[72:76].to01()
    self.combination = self.bitMessage[76:80].to01()
    self.bet = int(self.bitMessage[80:112].to01(), 2)
    self.ph = self.bitMessage[112:].to01()
    
  def print_me(self):
    print(self.marker)
    print(self.playerIp)
    print(self.playerPort)
    print(self.type)
    print(self.combination)
    print(self.bet)
    print(self.ph)
    print(self.message)

  def __validate(self):
    self.garbage = not self.message[0:8] == self.__START_MARKER

    if self.isGarbage():
      return
    
    ph = self.parity()
    if ph != self.message[112:].encode():
      self.garbage = True

  def isGarbage(self):
    chance = randrange(15)
    if(chance == 5):
      return True
    
    return self.garbage

  def parity(self): 
    count = 0
    for c in self.message[0:len(self.message)-1]:
      if c == '1':
        count += 1

    return str(count % 2).encode()

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
  def binaryMessage(self, playerIp, playerPort, type, combination, bet):
    assert isinstance(type, str)
    assert isinstance(combination, str)
    
    byteMessage = self.__START_MARKER.encode() + self.__encodeIp(playerIp) + self.__encodePort(playerPort) + type.encode() + combination.encode() + bin(bet)[2:].zfill(32).encode() + b'0'

    message = Message(byteMessage)

    ph = message.parity()

    return self.__START_MARKER.encode() + self.__encodeIp(playerIp) + self.__encodePort(playerPort) + type.encode() + combination.encode() + bin(bet)[2:].zfill(32).encode() + ph

def main():
  binMessage = Message.binaryMessage(
    '127.0.0.1',
    5000,
    '0000',
    '1111',
    80000
  )

  msg = Message(binMessage)

  print(msg.isGarbage())

if __name__ == '__main__':
  main()