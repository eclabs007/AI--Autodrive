from threading import Thread
import os
car_command_in_progress=False
prev_obj=""
def handle_obj(obj):
    global prev_obj
    if obj==prev_obj:
        return
    prev_obj=obj

    t=Thread(target=handle_obj_in_thread,args=(obj,))
    t.start()
def play_sound(obj):
    os.system("tts.sh \"And Make Sound \"")
    os.system("aplay   -D plughw:2,0 "+" ./wav/"+obj+".wav")
    
def handle_obj_in_thread(command):
    global car_control,car_command_in_progress
    if(car_command_in_progress==True):
        print("command in progress")
        return
    print(command)
    car_command_in_progress=True
###Action
    if (command=="bird") or (command=="cat") or (command=="dog") or (command=="horse") or (command=="sheep") or(command=="cow") or(command=="elephant") or(command=="bear") or (command=="zebra") or(command=="giraffe") or (command=="bicycle") or(command=="car")or(command=="motorcycle") or(command=="airplane")or(command=="bus")or(command=="train")or(command=="truck")or(command=="boat"):
        
        os.system("tts.sh \"I See a "+str(command)+"\"")
        play_sound(command)

    car_command_in_progress=False
