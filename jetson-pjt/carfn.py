import socket
from threading import Thread
import time
car_command_in_progress=False
class udp_cli:
    def __init__(self,ip,port) :
        self.ip=ip
        self.port=port
        self.socket=socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    def send_msg(self,msg):
        self.socket.sendto(str.encode(msg),(self.ip,self.port))

car_control=udp_cli("192.168.4.1",7777)
prev_cmd=0
def move_car(command):
    global prev_cmd
    if (prev_cmd=="s")and(command=="s"):
        return
    prev_cmd=command
    t=Thread(target=move_car_thread,args=(command,))
    t.start()

def move_car_thread(command):
    global car_control,car_command_in_progress
    if(car_command_in_progress):
        print("command in progress")
        return
    print(command)
    car_command_in_progress=True
    car_control.send_msg(command)
    time.sleep(DELAY)
    car_command_in_progress=False