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

  def __init__(self, ip, port):
    self.players = {}
    self.state = self._GREETINGS
    self.ip = ip
    self.port = port

  def updatePlayer(self, message):
    player = message.playerIp + ':' + str(message.playerPort)
    self.players[player] = message.bet

  def updateSelfPlayer(self, coin):
    player = self.ip + ':' + str(self.port)
    self.players[player] = coin

  def updateState(self, state):
    self.state = state

  def printPlayers(self):
    for key in self.players:
      print(key, ':', self.players[key])

def main(): 
  game = Game()
  print(game._BET_PRIZE[game._PAR])

if __name__ == '__main__':
  main()