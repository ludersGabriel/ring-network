from telnetlib import IP
import types
from message import Message
from game import Game
import socket
import sys

class Server:
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

  def listen(self, message):
    data, addr = self.sock.recvfrom(1024)
    received = Message(data)

    # Envia a mensagem até não retornar lixo
    while received.isGarbage():
      self.sock.sendto(message, (self.targetIp, self.targetPort))

      data, addr = self.sock.recvfrom(1024)
      received = Message(data)

    return received, data

  def send(self, message):
    self.sock.sendto(message, (self.targetIp, self.targetPort))

  def passBat(self, state = ''):
    # Passamos o bastão e atualizamos o estado da instância do jogo
    message = Message.binaryMessage(
      self.ip, 
      self.port,
      Message._PASSING_BAT,
      self.game._ANY,
      0
    )

    self.setBat(False)
    self.send(message)

  def greetings(self):
    # Cria a mensagem com seu saldo, IP e porta
    message = Message.binaryMessage(
      self.ip, 
      self.port,
      Message._UPDATE_PLAYER_BALANCE,
      self.game._ANY,
      self.initialCoin
    )

    self.send(message)

    self.listen(message)

    self.game.updateState(self.game._PLAYING)

  def playing(self):
    bet, howMuch = self.game.chooseBet()

    message = Message.binaryMessage(
      self.ip,
      self.port,
      Message._BETTING,
      bet,
      howMuch
    )

    self.send(message)

    self.listen()

  def loop(self):
    if self.game.state == self.game._GREETINGS:
      self.greetings()
    elif self.game.state == self.game._PLAYING:
      self.playing()

    self.passBat()
