from telnetlib import IP
from time import sleep
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
      Message._GREETING,
      self.game._ANY,
      self.initialCoin
    )

    self.send(message)

    rec, d =self.listen()
    self.game.printPlayer(rec)

    self.game.updateState(self.game._PLAYING)

  def playing(self):
    combination, howMuch = self.game.chooseBet()

    message = Message.binaryMessage(
      self.ip,
      self.port,
      Message._BETTING,
      combination,
      howMuch
    )

    self.send(message)

    rec, d = self.listen()

    if rec.playerId == self.id:
      won = self.game.makePlay(rec)
      messageType = Message._UPDATE_PLAYER_BALANCE
      newCoins = self.game.coins

      if(won):
        newCoins += self.game._BET_PRIZE[rec.combination] - rec.bet 
      else:
        newCoins -= rec.bet

      self.game.updateSelfPlayer(newCoins)

      if(self.game.coins <= 0):
        messageType = Message._END_GAME

      message = Message.binaryMessage(
        self.ip,
        self.port,
        messageType,
        self.game._ANY,
        self.game.coins
      )

      self.send(message)

      if(self.game.coins <= 0):
        print(f'Ops! Você zerou suas fichas. Fim do jogo!')
        print(f'Matando jogadores')

      self.listen()

      if(self.game.coins <= 0):
        print('Me matando')
        sys.exit()
        
    else:
      message = Message.binaryMessage(
        rec.playerIp,
        rec.playerPort,
        Message._CHOSEN_PLAYER,
        combination,
        rec.bet
      )

      self.send(message)

      print(f'Jogador {rec.playerId} cobriu sua aposta! Ele vai jogar')
      rec, d = self.listen()
      messageType = Message._UPDATE_PLAYER_BALANCE
      self.game.updatePlayer(rec)    

      if rec.bet <= 0:
        messageType = Message._END_GAME

      message = Message.binaryMessage(
        rec.playerIp,
        rec.playerPort,
        messageType,
        self.game._ANY,
        rec.bet
      )

      self.send(message)

      if rec.bet <= 0:
        print(f'Jogador {rec.playerId} zerou as fichas')
        print('Matando jogadores')

      self.listen()

      if rec.bet <= 0:
        print('Me matando')
        sys.exit()

    print('Fim do seu turno! Controle passado ao próximo jogador')

  def loop(self):
    if self.game.state == self.game._GREETINGS:
      self.greetings()
    elif self.game.state == self.game._PLAYING:
      self.playing()

    self.passBat()
