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

  def updatePlayer(self, message):
    player = message.playerIp + ':' + str(message.playerPort)
    self.players[player] = message.bet

  def updateSelfPlayer(self, coin):
    player = self.ip + ':' + str(self.port)
    self.players[player] = coin
    self.coins = coin

  def updateState(self, state):
    self.state = state

  def printPlayers(self):
    for key in self.players:
      print(key, ':', self.players[key])
    print(f'\t-> Seu saldo: {self.coins}\n')

  def chooseBet(self):
    self.printPlayers()

    for key in self._BETS_TEXT:
      print(f'{key}: {self._BETS_TEXT[key]}')
    bet = input('\nEscolha a sua jogada: ')
    
    howMuch = -1
    while(howMuch < 0 or howMuch > self.coins):
      howMuch = int(input(f'Quanto deseja apostar (0 <= x <= {self.coins}): '))

    return self._BETS[bet], howMuch


def main(): 
  game = Game()
  print(game._BET_PRIZE[game._PAR])

if __name__ == '__main__':
  main()