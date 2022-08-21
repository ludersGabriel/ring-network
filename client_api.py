from telnetlib import IP
import types
from message import Message
from game import Game
import socket
import sys

class Client:
  def __init__(self, ip, port, targetIp, taretPort, initialCoin, game, sock, setBat):
    assert isinstance(game, Game)
    assert isinstance(sock, socket.socket)
    assert isinstance(setBat, types.FunctionType)

    # Inicializa a classe
    self.ip = ip
    self.port = port
    self.targetIp = targetIp
    self.targetPort = taretPort
    self.initialCoin = initialCoin
    self.id = f'{ip}:{port}'

    self.game = game
    self.game.updateSelfPlayer(initialCoin)

    self.sock = sock
    self.setBat = setBat

  def listen(self):
    data, addr = self.sock.recvfrom(1024)
    received = Message(data)

    if received.type == Message._ERROR:
      print('Um erro ocorreu')
      print('Me matando')

      self.send(data)
      sys.exit()

    if received.isGarbage():
      print('Um erro ocorreu')
      print('Me matando')

      message = Message.binaryMessage(
        self.ip,
        self.port,
        Message._ERROR,
        self.game._ANY,
        self.game.coins
      )

      self.send(message)
      sys.exit()
    
    if received.type == Message._PASSING_BAT:
      self.setBat(True)

    return received, data

  # Tratamento da rodada inicial
  def greetings(self, received):
    assert isinstance(received, Message)

    # Atualiza a tabela ou recebe o bastão
    if received.type == Message._GREETING:
      self.game.updatePlayer(received, False)
      self.game.printPlayer(received)

  # Tratamento do jogo
  def playing(self, received, data):
    assert isinstance(received, Message)

    # Atualiza a tabela do jogo
    if received.type == Message._UPDATE_PLAYER_BALANCE:
      self.game.updatePlayer(received)

    elif received.type == Message._END_GAME:
      self.game.updatePlayer(received)

    elif received.type == Message._GREETING:
      self.game.updatePlayer(received, False)
      self.game.printPlayer(received)

    elif received.type == Message._BETTING:
      coverMessage = self.game.handleUpBet(received)
      if coverMessage:
        return coverMessage
      return data

    elif received.type == Message._CHOSEN_PLAYER and received.playerId == self.id:
      won = self.game.makePlay(received)
      messageType = Message._RESULT
      newCoins = self.game.coins

      if(won):
        newCoins += self.game._BET_PRIZE[received.combination] - received.bet 
      else:
        newCoins -= received.bet

      self.game.updateSelfPlayer(newCoins)
      message = Message.binaryMessage(
        self.ip,
        self.port,
        messageType,
        self.game._ANY,
        self.game.coins
      )

      return message

    return None

  def send(self, message):
    self.sock.sendto(message, (self.targetIp, self.targetPort))

  def loop(self):
    received, data = self.listen()
    if received.type == Message._ERROR:
      self.send(data)
      print('Um erro ocorreu em algum lugar')
      print('Me matando')
      sys.exit()

    if self.game.state == self.game._GREETINGS:
      self.greetings(received)
    elif self.game.state == self.game._PLAYING:
      newData = self.playing(received, data)
      if newData:
        data = newData

    if received.type == Message._END_GAME:
      self.send(data)
      print(f'Jogador {received.playerId} zerou as fichas')
      print('Me matando')
      sys.exit()

    if not received.type == Message._PASSING_BAT:
      self.send(data)