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

    self.ip = ip
    self.port = port
    self.targetIp = targetIp
    self.targetPort = taretPort
    self.initialCoin = initialCoin

    self.game = game
    self.game.updateSelfPlayer(initialCoin)

    self.sock = sock
    self.setBat = setBat

  def greetings(self):
    # Recebe uma mensagem com credenciais a serem atualizadas em sua tabela
    data, addr = self.sock.recvfrom(1024)
    received = Message(data)

    if received.isGarbage():
      self.sock.sendto(data, (self.targetIp, self.targetPort))

    if received.type == Message._UPDATE_PLAYER_BALANCE:
      self.game.updatePlayer(received)
    elif received.type == Message._PASSING_BAT:
      self.setBat(True)


    # Envia a mensagem que recebeu
    if not received.type == Message._PASSING_BAT:
      self.sock.sendto(data, (self.targetIp, self.targetPort))


