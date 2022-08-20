import struct
from bitarray import bitarray
import socket

# message format
# 10101011  | 
# MI 8b 0:8 | player ip 32b 8:40 | player port 32b 40:72 | type 4bits 72:76 | combination 4b 76:80 | bet 4b 80:112 | ph 1b 112:  

# Message types
# 1: message starting at the origin to choose who will roll the dice == 0001 (1)
# 2: message from origin to tell the player to make his play == 0010 (2)
# 3: message updating player balance == 0011 (3)
# 4: message to pass the bat -> is this a message? Does the bat has to be a struct? == 0100 (4)

class Message:
  __START_MARKER = '10101011'

  # message types
  _BETTING = '0001'
  _CHOSEN_PLAYER = '0010'
  _UPDATE_PLAYER_BALANCE = '0011'
  _PASSING_BAT = '0100' 

  def __init__(self, message):
    self.binMessage = message
    self.message = message.decode()
    
    self.__validate()

    if(self.isGarbage()): 
      return

    self.bitMessage = bitarray(self.message)
    self.marker = self.bitMessage[0:8].to01()

    # sets current player fields
    self.playerIp = self.__decodeIp(self.bitMessage[8:40])
    self.playerPort = self.__decodePort(self.bitMessage[40:72])

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

  def __validate(self):
    # If the message doesn't have the correct size, garbage is set to True.
    # if(len(self.message) < 85):
    #   self.garbage = True
    #   return

    self.garbage = not self.message[0:8] == self.__START_MARKER

  def isGarbage(self):
    return False

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
    return self.__START_MARKER.encode() + self.__encodeIp(playerIp) + self.__encodePort(playerPort) + type.encode() + combination.encode() + bin(bet)[2:].zfill(32).encode() + b'0'

def main():
  binMessage = Message.binaryMessage(
    '127.0.0.1',
    5000,
    '0000',
    '1111',
    80000
  )

  msg = Message(binMessage)

  if(msg.isGarbage()):
    return

  msg.print_me()
  print(msg.isGarbage())

if __name__ == '__main__':
  main()