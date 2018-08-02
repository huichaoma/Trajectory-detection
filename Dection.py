# coding:utf8
import cv2
import time
import threading

Cam_Width=0
Cam_Height=0

class Center:
    Rect_Center={ }#重心字典
    Len_Rect=0#记录重心个数
    Num_Fra=0#记录帧数
    __First_Signal=True
    Up_Deviation=0
    Down_Deviation=0
    Occupy_Signal=False
    def __init__(self,num,y_up,y_down):
        self.Len_Rect=0
        self.Num_Fra=num
        self.Rect_Center={i:[] for i in range(num)}
        self.Up_Deviation=y_up
        self.Down_Deviation=y_down
    def Judge_Center(self,Input_Rect_Center):
        #第一次收集数据
        if self.__First_Signal:
            self.__First_Signal=False
            self.Rect_Center[self.Len_Rect]=Input_Rect_Center
            self.Len_Rect+=1
            self.Occupy_Signal=True
        else:
            if(self.Len_Rect<15):
                if len(self.Rect_Center[0]):
                    #print(self.Rect_Center)
                    if Input_Rect_Center[4]<(self.Rect_Center[0][4]+self.Up_Deviation) or \
                           Input_Rect_Center[4]>(self.Rect_Center[0][4]-self.Down_Deviation):
                        self.Rect_Center[self.Len_Rect] = Input_Rect_Center
                        self.Len_Rect+=1
                        self.Occupy_Signal=True
        if self.Occupy_Signal and self.Len_Rect<self.Num_Fra:
            if len(self.Rect_Center[0]):
                 if(Input_Rect_Center[0]!=self.Rect_Center[0][0]):
                    self.Center_Clear()
                 else:
                    if(Input_Rect_Center[1]-self.Rect_Center[0][1])>1:
                        self.Center_Clear()
                    else:
                        if(Input_Rect_Center[2]-self.Rect_Center[0][2])>5:
                            print("Over Time")
                            self.Center_Clear()
        #print(self.Rect_Center)
        return self.Occupy_Signal
    def Center_Clear(self):
        for i in range(self.Num_Fra):
            self.Rect_Center[i].clear()
        self.Len_Rect = 0
        self.Occupy_Signal=False
        self.__First_Signal=True
def Center_Gravity(cnt):
    Gravity=[]
    M=cv2.moments(cnt)
    Gravity.append(int(M['m10']/M['m00']))
    Gravity.append(int(M['m01']/M['m00']))
    return Gravity
def Recording_Struct(frame,contours):
    Frame_Time=[0,0,0,0,0]
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        if (frame.shape[0]*frame.shape[1]//20) < area and area<(frame.shape[0]*frame.shape[1]//2):
            #cv2.drawContours(frame, c, -1, (0, 0, 255), 3)#画手势轮廓
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            circle = Center_Gravity(c) #计算重心
            Temp_Time = time.localtime(time.time())
            Frame_Time[0]=Temp_Time.tm_hour
            Frame_Time[1]=Temp_Time.tm_min
            Frame_Time[2]=Temp_Time.tm_sec
            Frame_Time[3]=circle[0]
            Frame_Time[4]=circle[1]
            cv2.circle(frame, tuple(circle), 5, (255, 0, 0), 5)  # 标记重心

            if not len(Frame_Time):
                continue
            elif Trajectory_1.Judge_Center(Frame_Time):
                Trajectory_1.Occupy_Signal=False
            elif Trajectory_2.Judge_Center(Frame_Time):
                Trajectory_2.Occupy_Signal=False
            #elif Trajectory_3.Judge_Center(Frame_Temp,circle):
            #    Trajectory_3.Occupy_Signal=False
            #elif Trajectory_4.Judge_Center(Frame_Temp,circle):
            #    Trajectory_4.Occupy_Signal=False
            #elif Trajectory_5.Judge_Center(Frame_Temp,circle):
            #    Trajectory_5.Occupy_Signal=False
    return frame,contours
def Dection_Effection(data,Len):
    Temp=[]
    Temp_Len=0
    i=0
    j=Len-1
    while i<j and data[i][0]!=data[j][0]:#可以省略
        if data[i+1][0]!=data[i][0]:
            i=i+1
        if data[j-1][0]!=data[j][0]:
            j=j-1
        if data[i+1][0]==data[i][0] and data[j-1][0]==data[j][0]:
            j=j-1
            i=i+1
    while i<j and data[i][1]!=data[j][1] :#可以省略
        if data[i+1][1]!=data[i][1]:
            i=i+1
        if data[j-1][1]!=data[j][1]:
            j=j-1
        if data[i+1][1]==data[i][1] and data[j-1][1]==data[j][1]:
            j=j-1
            i=i+1
    while  i<j and (data[j][2]-data[i][2])>1:
        if(data[i+1][2]-data[i][2])>1:
            i=i+1
        if(data[j][2]-data[j-1][2])>1:
            j=j-1
        if (data[i+1][2]-data[i][2])<=1 and (data[j][2]-data[j-1][2])<=1:
            i=i+1
            j=j-1
    if i>=j:
        if (data[i-1][3]-data[0][3])>=(data[Len-1][3]-data[j][3]):
            j=i-1
            i=0
        else:
            i=j+1
            j=Len-1
    while i<=j:
        Temp.append(data[i][3])
        Temp_Len+=1
        i+=1
    return Temp,Temp_Len
def Judgement():
    global Cam_Width
    if Trajectory_1.Len_Rect>=15:
        Effective,Len_E=Dection_Effection(Trajectory_1.Rect_Center,Trajectory_1.Len_Rect)
        if(Effective[Len_E-1]-Effective[0])>(int(0.4*Cam_Width)):
            print("Right")
            print("Effective:", Effective)
        if (Effective[0]-Effective[Len_E-1]) > (int(0.4*Cam_Width)):
            print("Left")
            print("Effective:", Effective)
        Trajectory_1.Center_Clear()
    if Trajectory_2.Len_Rect>=15:
        Effective_1, Len_E_1 = Dection_Effection(Trajectory_2.Rect_Center, Trajectory_2.Len_Rect)
        if (Effective_1[Len_E_1-1] - Effective_1[0]) > (int(0.4 * Cam_Width)):
            print("Right")
            print("Effective_1:",Effective_1)
        if (Effective_1[0] - Effective_1[Len_E_1-1]) > (int(0.4 * Cam_Width)):
            print("Left")
            print("Effective_1:", Effective_1)
        Trajectory_2.Center_Clear()
    '''
    if Trajectory_3.Len_Rect>=15:
        if (Trajectory_3.Rect_Center[Trajectory_3.Len_Rect - 1][0] - Trajectory_3.Rect_Center[0][0]) > (int(0.5*Cam_Width)):
            if Trajectory_3.To_Right_Signal and (not Trajectory_3.To_Left_Signal):
                print("Right")
        if (Trajectory_3.Rect_Center[0][0] - Trajectory_3.Rect_Center[Trajectory_3.Len_Rect - 1][0]) > (int(0.5*Cam_Width)):
            if Trajectory_3.To_Left_Signal and (not Trajectory_3.To_Right_Signal):
                print("Left")
        Trajectory_3.Center_Clear()
    if Trajectory_4.Len_Rect>=15:
        if (Trajectory_4.Rect_Center[Trajectory_4.Len_Rect - 1][0] - Trajectory_4.Rect_Center[0][0]) > (int(0.5*Cam_Width)):
            if Trajectory_4.To_Right_Signal and (not Trajectory_4.To_Left_Signal):
                print("Right")
        if (Trajectory_4.Rect_Center[0][0] - Trajectory_4.Rect_Center[Trajectory_4.Len_Rect - 1][0]) > (int(0.5*Cam_Width)):
            if Trajectory_4.To_Left_Signal and (not Trajectory_4.To_Right_Signal):
                print("Left")
        Trajectory_4.Center_Clear()
    if Trajectory_5.Len_Rect>=15:
        if (Trajectory_5.Rect_Center[Trajectory_5.Len_Rect - 1][0] - Trajectory_5.Rect_Center[0][0]) > (int(0.5*Cam_Width)):
            if Trajectory_5.To_Right_Signal and (not Trajectory_5.To_Left_Signal):
                print("Right")
        if (Trajectory_5.Rect_Center[0][0] - Trajectory_5.Rect_Center[Trajectory_5.Len_Rect - 1][0]) > (int(0.5*Cam_Width)):
            if Trajectory_5.To_Left_Signal and (not Trajectory_5.To_Right_Signal):
                print("Left")
        Trajectory_5.Center_Clear()
     '''
def detect_video():
    global  Number_Frame,Cam_Width,Cam_Height
    res, frame = camera.read()
    frame = cv2.flip(frame, 1)
    Cam_Height=frame.shape[0]
    Cam_Width=frame.shape[1]
    #time.sleep(0.01)
    Number_Frame+=1
    fg_mask = bs.apply(frame)  # 获取 foreground mask
    # 对原始帧进行膨胀去噪
    th = cv2.threshold(fg_mask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
    th = cv2.erode(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
    dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 3)), iterations=2)
    # 获取所有检测框
    image, contours, hier = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if Number_Frame%1==0:#控制帧数
        Recording_Struct(frame, contours)
        Judgement()
    cv2.imshow("detection", frame)
    cv2.imshow("back", dilated)

if __name__ == '__main__':
    Trajectory_1 = Center(15,20,20)
    Trajectory_2 = Center(15,20,20)
    #Trajectory_3 = Center(15)
    #Trajectory_4 = Center(15)
    #Trajectory_5 = Center(15)
    camera = cv2.VideoCapture(0)
    history = 20  # 训练帧数
    bs = cv2.createBackgroundSubtractorKNN(detectShadows=True)  # 背景减除器，设置阴影检测
    bs.setHistory(history)
    Number_Frame=0
    while True:
        detect_video()
        if(Number_Frame==100):
            Number_Frame=0
        key=cv2.waitKey(5)&0xFF
        if(key==27):
            break
    camera.release()
    cv2.destroyAllWindows()
