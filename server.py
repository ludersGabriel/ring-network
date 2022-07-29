import base64
import socket
import sys
import time

def main():
  if(len(sys.argv) < 6):
    print('Usage: ./server ip port targetIp targetPort bat')
    sys.exit()
  
  UDP_IP = sys.argv[1]
  PORT = int(sys.argv[2])
  TARGET_IP = sys.argv[3]
  TARGET_PORT = int(sys.argv[4])
  bat = int(sys.argv[5])
  MESSAGE = b'Hello from ' + UDP_IP.encode() + b':' + sys.argv[2].encode()

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind((UDP_IP, PORT))


  print(f'Listening at {UDP_IP}:{PORT}')
  while True: 
    if(bat):
      sock.sendto(MESSAGE, (TARGET_IP, TARGET_PORT))
      print(f'Sent message "{MESSAGE}" to "{TARGET_IP}:{TARGET_PORT}"')
      print(f'Waiting response...')
      data, addr = sock.recvfrom(1024)
      print(f'Received message "{data}" from "{addr}"\n')
    else:
      print(f'Waiting message...')
      data, addr = sock.recvfrom(1024)
      print(f'Received message "{data}" from "{addr}"')
      time.sleep(3)
      sock.sendto(MESSAGE, (TARGET_IP, TARGET_PORT))
      print(f'Responded with "{MESSAGE}" to "{TARGET_IP}:{TARGET_PORT}"\n')
    time.sleep(5)
  
if __name__ == '__main__':
  main()