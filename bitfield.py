from bitarray import bitarray

class Message:
  def __init__(self, barray):
    self.type = barray[0:3]
    self.size = barray[3:6]
    self.data = barray[6:]
    
  def print_me(self):
    print(self.type)
    print(self.size)
    print(self.data)

def main():
  ba = bitarray('111010000')
  msg = Message(ba)
  msg.print_me()
  
  

if __name__ == '__main__':
  main()