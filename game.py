import os
from random import randrange
from time import sleep
from message import Message

class Game:
  _ANY = '0000'
  _PAR = '0001'
  _TRINCA = '0010'
  _DOIS_PARES = '0011' 
  _FULL_HOUSE = '0100' 
  _SEQ_BAIXA = '0101' 
  _SEQ_ALTA = '0110' 
  _QUADRA = '0111' 
  _QUINTETO = '1000' 

  _BETS_TEXT = {
    '1': 'Par',
    '2': 'Trinca',
    '3': 'Dois Pares',
    '4': 'Full House',
    '5': 'Sequencia baixa',
    '6': 'Sequencia alta',
    '7': 'Quadra', 
    '8': 'Quinteto'
  }

  _BETS = {
    '1': _PAR,
    '2': _TRINCA, 
    '3': _DOIS_PARES,
    '4': _FULL_HOUSE,
    '5': _SEQ_BAIXA,
    '6': _SEQ_ALTA, 
    '7': _QUADRA, 
    '8': _QUINTETO
  }

  _BET_PRIZE = {
    '0001': 2,
    '0010': 3,
    '0011': 4,
    '0100': 5,
    '0101': 7,
    '0110': 7,
    '0111': 10,
    '1000': 15
  }

  _GREETINGS = 0
  _PLAYING = 1
  _ENDING = 2

  def __init__(self, ip, port, initialCoins):
    self.players = {}
    self.state = self._GREETINGS
    self.ip = ip
    self.port = port
    self.updateSelfPlayer(initialCoins)
    self.dice = []
    for i in range(5):
      self.dice.append({
        'value': 0,
        'locked': False
      })

  def updatePlayer(self, message, table = True):
    player = message.playerIp + ':' + str(message.playerPort)
    self.players[player] = message.bet

    if table:
      self.printPlayers()

  def updateSelfPlayer(self, coin):
    player = self.ip + ':' + str(self.port)
    self.players[player] = coin
    self.coins = coin

  def updateState(self, state):
    self.state = state

  def printPlayers(self):
    os.system('clear')
    for key in self.players:
      print(key, ':', self.players[key])
    print(f'\t-> Seu saldo: {self.coins}\n')

  def printPlayer(self, message):
    assert isinstance(message, Message)
    print(f'{message.playerId}: {message.bet}')

  def betPrize(self, key):
    return f'{self._BETS_TEXT[key]} ({self._BET_PRIZE[bin(int(key))[2:].zfill(4)]})'

  def chooseBet(self):
    self.printPlayers()

    for key in self._BETS_TEXT:
      print(f'{key}: {self.betPrize(key)}')
    print()

    bet = -1
    while bet < 1 or bet > 8:
      inp = input('Escolha a sua jogada ao custo de 1 ficha: ')
      if(inp):
        bet = int(inp)
      else:
        bet = -1

    # Pela especificação, o custo é fixo em 1
    # howMuch = -1
    # while(howMuch < 0 or howMuch > self.coins):
    #   howMuch = int(input(f'Quanto deseja apostar (0 <= x <= {self.coins}): '))

    return self._BETS[str(bet)], 1

  def handleUpBet(self, message):
    assert isinstance(message, Message)

    self.printPlayers()

    print(
      f'A aposta atual é de {message.bet} ' + 
      f'em {self.betPrize(str(int(message.combination, 2)))} por {message.playerId}'
    )
    
    cover = -1
    if message.bet < self.coins:
      while cover != 0 and (cover < 0 or cover > self.coins or cover <= message.bet):
        inp = input(
          f'Para cobrir a aposta, entre com um valor {message.bet} <' +
          f' x <= {self.coins}. 0 caso contrário: '
        )
        if inp:
          cover = int(inp)
        else:
          cover = -1
    else:
      print(
        f'Seu saldo é menor que a aposta feita, impossível cobrir. Passando o turno'
      )

    if cover > message.bet:
      return Message.binaryMessage(
        self.ip,
        self.port,
        Message._BETTING,
        message.combination,
        cover
      )
      
    return None

  def ___convertFunction(self, a):
    return a['value']

  def rollDice(self):
    for el in self.dice:
      if not el['locked']:
        el['value'] = randrange(6) + 1
    rolagem = list(map(self.___convertFunction, self.dice))

    print(f'Sua rolagem foi: ', end='')
    print(*(rolagem), sep=', ')

    return rolagem

  def lockDice(self, lst):
    assert isinstance(lst, list)
    for i in lst:
      self.dice[i]['locked'] = True

  def verifyPar(self, roll):
    for key in roll:
      if roll[key] >= 2: 
        return True
    return False

  def verifyTrinca(self, roll):
    for key in roll:
      if roll[key] >= 3: 
        return True
    return False

  def verifyDoisPares(self, roll):
    for key in roll:
      if roll[key] == 4:
        return True
      elif roll[key] >= 2: 
        roll[key] -= 2
        break
    
    for key in roll:
      if roll[key] == 4 or roll[key] == 2:
        return True
    
    return False

  def verifyFullHouse(self, roll):
    for key in roll:
      if roll[key] >= 3: 
        roll[key] = 0
        break
    
    for key in roll:
      if roll[key] >= 2:
        return True
    
    return False

  def verifySeqBaixa(self, dice):
    seq = sorted(dice)

    j = 1
    i = 0
    while i < len(seq):
      if seq[i] != j:
        return False
      i += 1
      j += 1
    
    return True

  def verifySeqAlta(self, dice):
    seq = sorted(dice)

    j = 2
    i = 0
    while i < len(seq):
      if seq[i] != j:
        return False
      i += 1
      j += 1
    
    return True

  def verifyQuadra(self, roll):
    for key in roll:
      if roll[key] >= 4:
        return True
    
    return False

  def verifyQuinteto(self, roll):
    for key in roll:
      if roll[key] >= 5:
        return True
    
    return False

  def verifyPlay(self, combination, rolagem):
    verified = False
    roll = {}
    for el in rolagem:
      key = str(el)
      if key in roll: 
        roll[key] = roll[key] + 1
      else:
        roll[key] = 1

    # debug code
    # for key in roll:
    #   print(f'{key}:{roll[key]}')
    # print()

    if combination == self._PAR:
      verified = self.verifyPar(roll)
    elif combination == self._TRINCA:
      verified = self.verifyTrinca(roll)
    elif combination == self._DOIS_PARES:
      verified = self.verifyDoisPares(roll)
    elif combination == self._FULL_HOUSE:
      verified = self.verifyFullHouse(roll)
    elif combination == self._SEQ_BAIXA:
      verified = self.verifySeqBaixa(rolagem)
    elif combination == self._SEQ_ALTA:
      verified = self.verifySeqAlta(rolagem)
    elif combination == self._QUADRA:
      verified = self.verifyQuadra(roll)
    elif combination == self._QUINTETO:
      verified = self.verifyQuinteto(roll)

    return verified

  def makePlay(self, received):
    assert isinstance(received, Message)

    print('\nVocê é o jogador da vez! Rolando os dados')
    rolagem = self.rollDice()
    for i in range(2):
      lst = input('Quais dados deseja bloquear (1,2,3,4,5), separados por espaço: ').split()
      lst = [int(num) for num in lst]

      while len(lst) > 0 and (len(lst) > 5 or max(lst) > 5 or min(lst) < 1):

        lst = input('Quais dados deseja bloquear (1,2,3,4,5), separados por espaço: ').split()
        lst = [int(num) for num in lst]
      lst = [num - 1 for num in lst]
      self.lockDice(lst)

      rolagem = self.rollDice()

    ret = self.verifyPlay(received.combination, rolagem)
    if ret:
      print(
        f'Voce ganhou a rolagem! Seu premio é: '+
        f'{self._BET_PRIZE[received.combination] - received.bet}'
      )
    else:
      print(f'voce perdeu a rolagem! {received.bet} fichas descontadas')  
    
    sleep(2)
    return ret

def main(): 
  game = Game('127.0.0.1', 5555, 5)
  print(game.verifyPlay(game._PAR, [2,1,1,4,5]))
  print(game.verifyPlay(game._TRINCA, [2,1,1,1,5]))
  print(game.verifyPlay(game._DOIS_PARES, [2,1,1,4,4]))
  print(game.verifyPlay(game._DOIS_PARES, [2,1,1,1,1]))
  print(game.verifyPlay(game._FULL_HOUSE, [2,2,3,3,3]))
  print(game.verifyPlay(game._FULL_HOUSE, [5,5,5,5,5]))


if __name__ == '__main__':
  main()