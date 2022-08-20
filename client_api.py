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

    self.game = game
    self.game.updateSelfPlayer(initialCoin)

    self.sock = sock
    self.setBat = setBat

  def listen(self):
    data, addr = self.sock.recvfrom(1024)
    received = Message(data)

    if received.isGarbage():
      self.sock.sendto(data, (self.targetIp, self.targetPort))
    
    if received.type == Message._PASSING_BAT:
      self.setBat(True)

    return received, data

  # Tratamento da rodada inicial
  def greetings(self, received):
    assert isinstance(received, Message)

    # Atualiza a tabela ou recebe o bastão
    if received.type == Message._UPDATE_PLAYER_BALANCE:
      self.game.updatePlayer(received)

  # Tratamento do jogo
  def playing(self, received):
    assert isinstance(received, Message)

    # Atualiza a tabela do jogo
    if received.type == Message._UPDATE_PLAYER_BALANCE:
      self.game.updatePlayer(received)
    elif received.type == Message._BETTING:
      # do something
      pass

  def loop(self):
    received, data = self.listen()

    if self.game.state == self.game._GREETINGS:
      self.greetings(received)
    elif self.game.state == self.game._PLAYING:
      self.playing(received)

    if not received.type == Message._PASSING_BAT:
      self.sock.sendto(data, (self.targetIp, self.targetPort))