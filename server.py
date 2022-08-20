import socket
import sys
from game import Game
from message import Message
from client_api import Client
from server_api import Server

if(len(sys.argv) < 6):
  print('Usage: ./server ip port targetIp targetPort initialCoin bat')
  sys.exit()

UDP_IP = sys.argv[1]
PORT = int(sys.argv[2])
TARGET_IP = sys.argv[3]
TARGET_PORT = int(sys.argv[4])
INITIAL_COIN = int(sys.argv[5])
BAT = int(sys.argv[6])  

def setBat(value):
  global BAT
  BAT = value

def main():
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind((UDP_IP, PORT))

  game = Game(UDP_IP, PORT)
  game.updateSelfPlayer(INITIAL_COIN)

  server = Server(
    UDP_IP,
    PORT,
    TARGET_IP,
    TARGET_PORT,
    INITIAL_COIN,
    game,
    sock,
    setBat
  )

  client = Client(
    UDP_IP,
    PORT,
    TARGET_IP,
    TARGET_PORT,
    INITIAL_COIN,
    game,
    sock,
    setBat
  )

  while True: 
    if(game.state == game._GREETINGS):
      # Cria a mensagem com suas credenciais
      if BAT:
        server.greetings()
      else:
        client.greetings()       
    elif(game.state == game._PLAYING):
      if BAT: 
        pass
      else:
        game.printPlayers()
        print()
        data, addr = sock.recvfrom(1024)
        received = Message(data)

        if not received.isGarbage():
          if received.type == Message._UPDATE_PLAYER_BALANCE:
            game.updatePlayer(received)

        if not received.type == Message._PASSING_BAT:
          sock.sendto(data, (TARGET_IP, TARGET_PORT))
    elif(game.state == game._ENDING):
      if BAT: 
        pass
      else:
        pass
  
  
if __name__ == '__main__':
  main()