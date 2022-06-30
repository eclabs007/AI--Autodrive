import cv2
import time
import jetson.inference as ji
import jetson.utils as ju
import os


import carfn
import ent 
MODE="DRIVE"

offw=98
yt=370
DELAY=0.1
net=ji.detectNet("ssd-mobilenet-v2",threshold=0.4)
def nothing(x):
    print(x)

window_title = "CSI Camera"

#gst_pipe="nvarguscamerasrc sensor-id=0 !video/x-raw(memory:NVMM), width=224, height=224 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=true "
gst_pipe="nvarguscamerasrc sensor-id=0 !video/x-raw(memory:NVMM), width=640, height=480 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=true "
video_capture = cv2.VideoCapture(gst_pipe, cv2.CAP_GSTREAMER)




from flask import  Flask, Response ,request, render_template

app=Flask(__name__)
@app.route('/',methods = ['GET', 'POST'])
def home():
    global yt,offw,DELAY,MODE
    if request.method == 'POST':
        os.system("killall -9 aplay")
        if request.form['submit_button'] == 'DRIVE':
            os.system("tts.sh \" ENTERTAINMENT\"")
            MODE='ENT'
        if request.form['submit_button'] == 'ENT':
            MODE='DRIVE'
            os.system("tts.sh \" DRIVE\"")
        if request.form['submit_button'] == 'yt+':
            yt=yt+10
        if request.form['submit_button'] == 'yt-':
            yt=yt-10
        if request.form['submit_button'] == 'w-':
            offw=offw-10
        if request.form['submit_button'] == 'w+':
            offw=offw+10
        if request.form['submit_button'] == 'del-':
            DELAY=DELAY-0.1
        if request.form['submit_button'] == 'del+':
            DELAY=DELAY+0.1

        if request.form['submit_button'] == 'song1':
            os.system("aplay   -D plughw:2,0  ./wav/song1.wav &")
        if request.form['submit_button'] == 'song2':
            os.system("aplay   -D plughw:2,0  ./wav/song2.wav &")
        if request.form['submit_button'] == 'song3':
            os.system("aplay   -D plughw:2,0  ./wav/song3.wav &")
            

        print("New values of yt,w,del="+str(yt)+","+str(offw)+","+str(DELAY))
    rndr_data=dict(yt=yt,w=offw,delay=DELAY,mod=MODE)

    return render_template("home.html",**rndr_data)

@app.route('/live')
def live():
    return Response(main(),mimetype='multipart/x-mixed-replace;boundary=frame')

def main():
    global yt,offw
   
    while True:
        s=time.time()
        ret_val, img = video_capture.read()
        try:
            w=img.shape[1]
            h=img.shape[0]
        except:
            print("No Video available")
            os.sytem("sudo systemctl restart nvargus-daemon.service")
            continue
        

        im_cuda=ju.cudaFromNumpy(img)
        det=net.Detect(im_cuda)

    
        img = cv2.line(img,(0,yt),(int(w),yt),(0,255,0),1)
        img = cv2.line(img,(int(w/2)-offw,0),(int(w/2)-offw,h),(0,255,255),5)
        img = cv2.line(img,(int(w/2)+offw,0),(int(w/2)+offw,h),(0,255,255),5)
        if MODE=="DRIVE":
            for d in det:
                #print(d)
                x1,y1,x2,y2=int(d.Left),int(d.Top),int(d.Right),int(d.Bottom)
                className=net.GetClassDesc(d.ClassID)
        
                if str(className)=="person":
                    cx=int(abs(x2-x1)/2)+x1
                    cy=int(abs(y2-y1)/2)+y1
                    cv2.circle(img,(cx,cy),10,color=(100,0,0),thickness=5)
                    cv2.rectangle(img,(x1,y1),(x2,y2),color=(0,0,255),thickness=5)

                    if(y2>=yt):
                        carfn.move_car("s")
                    elif cx<(int(w/2)-offw):
                        carfn.move_car("L")
                    elif cx>(int(w/2)+offw):
                        carfn.move_car("R")
                    elif(y2<yt):
                        carfn.move_car("f")
        else:
            prev_Confidence=0
            Confidence=0
            className=""
            for d in det:
                
                Confidence=d.Confidence
                if Confidence>prev_Confidence:
                    prev_Confidence=Confidence
                    x1,y1,x2,y2=int(d.Left),int(d.Top),int(d.Right),int(d.Bottom)
                    className=net.GetClassDesc(d.ClassID)

            if(className!=""):
                ent.handle_obj(str(className))               
                cv2.rectangle(img,(x1,y1),(x2,y2),color=(0,0,255),thickness=5)



        ret,jpeg=cv2.imencode('.jpg',img)
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'+jpeg.tobytes()+b'\r\n\r\n')
        #cv2.imshow(window_title, img)
        #cv2.waitKey(1) 
        e=time.time()
        fps=round(1/(e-s))
        #print(fps)


if __name__=='__main__':
    os.system("tts.sh   Started")
    app.run(host='0.0.0.0',port=7000,threaded=True)
    main()
    os.system("tts.sh \" EXIT\"")
