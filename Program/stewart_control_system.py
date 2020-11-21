from Tkinter import Frame, Tk, BOTH, Text, Menu, END, Button, Label
import tkFont
import tkFileDialog
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
import time

style.use("ggplot")
   
class Run(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initConfig()
        self.initUI()

    def initConfig(self):
        self.run = False
        self.lastText = np.array(["450.00","450.00","450.00","450.00","450.00","450.00","0.00","0.00","0.00","0.00","0.00","0.00"])

        self.L = np.array([[float(self.lastText[0]),float(self.lastText[1]),float(self.lastText[2]),float(self.lastText[3]),float(self.lastText[4]),float(self.lastText[5])]])

        # motor parameter
        self.Bm = 1.15
        self.Jm = 0.18
        self.Km = 0.01
        
        # PID parameter
        self.KP_L = 20
        
        self.KP_L_dot = 200
        self.TI_L_dot = 2
        self.TD_L_dot = 0.0
        
        # delta time 
        self.dt = 0.01
		

    def initUI(self):
        self.parent.title("5 AXIS STEWART CNC G-CODE READER")
        self.pack(fill=BOTH, expand=1)
        self.line = 1.0
        self.maxLine = 1.0

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        fileMenu.add_command(label="Clear", command=self.onClear)
        fileMenu.add_command(label="Save", command=self.onSave)
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)

        runMenu = Menu(menubar)
        runMenu.add_command(label="Initialize", command=self.onInit)
        runMenu.add_command(label="Run/Pause", command=self.onRun)
        runMenu.add_command(label="Stop", command=self.onStop)
        menubar.add_cascade(label="Run", menu=runMenu)

        self.execButton = Button(self, text="Execute", command=self.onExec)
        self.execButton.place(x=950, y=20)

        self.prevButton = Button(self, text="Prev", command=self.onPrev)
        self.prevButton.place(x=1080, y=20)

        self.nextButton = Button(self, text="Next", command=self.onNext)
        self.nextButton.place(x=1140, y=20)

        self.notif = "Application Started"

        self.lblNC = Label(self, text="NC")
        self.lblNC.place(x=10, y=0)

        self.lblL = Label(self, text="Link Length        -        Link Length/sec")
        self.lblL.place(x=930, y=80)
        self.lblL1 = Label(self, text="1 :                         mm                                  mm/s")
        self.lblL1.place(x=900, y=120)
        self.lblL2 = Label(self, text="2 :                         mm                                  mm/s")
        self.lblL2.place(x=900, y=150)
        self.lblL3 = Label(self, text="3 :                         mm                                  mm/s")
        self.lblL3.place(x=900, y=180)
        self.lblL4 = Label(self, text="4 :                         mm                                  mm/s")
        self.lblL4.place(x=900, y=210)
        self.lblL5 = Label(self, text="5 :                         mm                                  mm/s")
        self.lblL5.place(x=900, y=240)
        self.lblL6 = Label(self, text="6 :                         mm                                  mm/s")
        self.lblL6.place(x=900, y=270)

        self.txtNC = Text(self, width=120, height=17)
        self.txtNC.place(x=10, y=20)
        self.txtNC.tag_configure('highlightline', background="#a9e9e9")
        self.txtNC.config(font=("TkTextFont", 10))
        self._highlight_current_line()
        
        self.txtL1 = Text(self, width=10, height=1)
        self.txtL1.place(x=930, y=120)
        self.txtL2 = Text(self, width=10, height=1)
        self.txtL2.place(x=930, y=150)
        self.txtL3 = Text(self, width=10, height=1)
        self.txtL3.place(x=930, y=180)
        self.txtL4 = Text(self, width=10, height=1)
        self.txtL4.place(x=930, y=210)
        self.txtL5 = Text(self, width=10, height=1)
        self.txtL5.place(x=930, y=240)
        self.txtL6 = Text(self, width=10, height=1)
        self.txtL6.place(x=930, y=270)

        self.txtL1Dot = Text(self, width=10, height=1)
        self.txtL1Dot.place(x=1090, y=120)
        self.txtL2Dot = Text(self, width=10, height=1)
        self.txtL2Dot.place(x=1090, y=150)
        self.txtL3Dot = Text(self, width=10, height=1)
        self.txtL3Dot.place(x=1090, y=180)
        self.txtL4Dot = Text(self, width=10, height=1)
        self.txtL4Dot.place(x=1090, y=210)
        self.txtL5Dot = Text(self, width=10, height=1)
        self.txtL5Dot.place(x=1090, y=240)
        self.txtL6Dot = Text(self, width=10, height=1)
        self.txtL6Dot.place(x=1090, y=270)

        self.f = Figure(figsize=(13.0, 3.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.f,self)
        self.canvas.draw()

#        self.ax = Axes3D(self.f)
#        self.ax.mouse_init()
#        self.set_ax()        
        self.canvas.get_tk_widget().place(x=10, y=350)
        
    def extractNC(self):
        self.extractL1()
        self.extractL2()
        self.extractL3()
        self.extractL4()
        self.extractL5()
        self.extractL6()
        self.extractL1Dot()
        self.extractL2Dot()
        self.extractL3Dot()
        self.extractL4Dot()
        self.extractL5Dot()
        self.extractL6Dot()
        
    def extractL1(self):
        try:
            posL1 = self.txtNC.search("LA", self.line, str(int(self.line)) + '.end',8)
            textL1 = self.txtNC.get(posL1 + '+2c', posL1 + '+8c')
            self.txtL1.insert(1.0, textL1)
            self.lastText[0] = textL1
        except:
            self.txtL1.insert(1.0, self.lastText[0])
        return (self.txtL1.get(1.0, 'end'))

    def extractL2(self):
        try:
            posL2 = self.txtNC.search("LB", self.line, str(int(self.line)) + '.end',8)
            textL2 = self.txtNC.get(posL2 + '+2c', posL2 + '+8c')
            self.txtL2.insert(1.0, textL2)
            self.lastText[1] = textL2
        except:
            self.txtL2.insert(1.0, self.lastText[1])
        return (self.txtL2.get(1.0, 'end'))

    def extractL3(self):
        try:
            posL3 = self.txtNC.search("LC", self.line, str(int(self.line)) + '.end',8)
            textL3 = self.txtNC.get(posL3 + '+2c', posL3 + '+8c')
            self.txtL3.insert(1.0, textL3)
            self.lastText[2] = textL3
        except:
            self.txtL3.insert(1.0, self.lastText[2])
        return (self.txtL3.get(1.0, 'end'))

    def extractL4(self):
        try:
            posL4 = self.txtNC.search("LD", self.line, str(int(self.line)) + '.end',8)
            textL4 = self.txtNC.get(posL4 + '+2c', posL4 + '+8c')
            self.txtL4.insert(1.0, textL4)
            self.lastText[3] = textL4
        except:
            self.txtL4.insert(1.0, self.lastText[3])
        return (self.txtL4.get(1.0, 'end'))

    def extractL5(self):
        try:
            posL5 = self.txtNC.search("LE", self.line, str(int(self.line)) + '.end',8)
            textL5 = self.txtNC.get(posL5 + '+2c', posL5 + '+8c')
            self.txtL5.insert(1.0, textL5)
            self.lastText[4] = textL5
        except:
            self.txtL5.insert(1.0, self.lastText[4])
        return (self.txtL5.get(1.0, 'end'))

    def extractL6(self):
        try:
            posL6 = self.txtNC.search("LF", self.line, str(int(self.line)) + '.end',8)
            textL6 = self.txtNC.get(posL6 + '+2c', posL6 + '+8c')
            self.txtL6.insert(1.0, textL6)
            self.lastText[5] = textL6
        except:
            self.txtL6.insert(1.0, self.lastText[5])
        return (self.txtL6.get(1.0, 'end'))
                
    def extractL1Dot(self):
        try:
            posL1Dot = self.txtNC.search("dLA", self.line, str(int(self.line)) + '.end',8)
            textL1Dot = self.txtNC.get(posL1Dot + '+3c', posL1Dot + '+8c')
            self.txtL1Dot.insert(1.0, textL1Dot)
            self.lastText[6] = textL1Dot
        except:
            self.txtL1Dot.insert(1.0, self.lastText[6])
        return (self.txtL1Dot.get(1.0, 'end'))

    def extractL2Dot(self):
        try:
            posL2Dot = self.txtNC.search("dLB", self.line, str(int(self.line)) + '.end',8)
            textL2Dot = self.txtNC.get(posL2Dot + '+3c', posL2Dot + '+8c')
            self.txtL2Dot.insert(1.0, textL2Dot)
            self.lastText[7] = textL2Dot
        except:
            self.txtL2Dot.insert(1.0, self.lastText[7])
        return (self.txtL2Dot.get(1.0, 'end'))

    def extractL3Dot(self):
        try:
            posL3Dot = self.txtNC.search("dLC", self.line, str(int(self.line)) + '.end',8)
            textL3Dot = self.txtNC.get(posL3Dot + '+3c', posL3Dot + '+8c')
            self.txtL3Dot.insert(1.0, textL3Dot)
            self.lastText[8] = textL3Dot
        except:
            self.txtL3Dot.insert(1.0, self.lastText[8])
        return (self.txtL3Dot.get(1.0, 'end'))

    def extractL4Dot(self):
        try:
            posL4Dot = self.txtNC.search("dLD", self.line, str(int(self.line)) + '.end',8)
            textL4Dot = self.txtNC.get(posL4Dot + '+3c', posL4Dot + '+8c')
            self.txtL4Dot.insert(1.0, textL4Dot)
            self.lastText[9] = textL4Dot
        except:
            self.txtL4Dot.insert(1.0, self.lastText[9])
        return (self.txtL4Dot.get(1.0, 'end'))

    def extractL5Dot(self):
        try:
            posL5Dot = self.txtNC.search("dLE", self.line, str(int(self.line)) + '.end',8)
            textL5Dot = self.txtNC.get(posL5Dot + '+3c', posL5Dot + '+8c')
            self.txtL5Dot.insert(1.0, textL5Dot)
            self.lastText[10] = textL5Dot
        except:
            self.txtL5Dot.insert(1.0, self.lastText[10])
        return (self.txtL5Dot.get(1.0, 'end'))

    def extractL6Dot(self):
        try:
            posL6Dot = self.txtNC.search("dLF", self.line, str(int(self.line)) + '.end',8)
            textL6Dot = self.txtNC.get(posL6Dot + '+3c', posL6Dot + '+8c')
            self.txtL6Dot.insert(1.0, textL6Dot)
            self.lastText[11] = textL6Dot
        except:
            self.txtL6Dot.insert(1.0, self.lastText[11])
        return (self.txtL6Dot.get(1.0, 'end'))

    def extractT(self):
        posT= self.txtNC.search("T", self.line, str(int(self.line)) + '.end',8)
        return (float(self.txtNC.get(posT + '+1c', posT + '+4c')))
      
    def _highlight_current_line(self, interval=100):
        '''Updates the 'current line' highlighting every "interval" milliseconds'''
        self.txtNC.tag_remove('highlightline', 1.0, "end")
        self.txtNC.tag_add('highlightline', self.line, str(int(self.line)) +'.end+1c' )
        self.after(interval, self._highlight_current_line)
    
    def draw(self):
        self.f.clear()
        self.f.add_subplot(2,6,1).set_ylim([-30,30])
        self.f.add_subplot(2,6,2).set_ylim([-30,30])
        self.f.add_subplot(2,6,3).set_ylim([-30,30])
        self.f.add_subplot(2,6,4).set_ylim([-30,30])
        self.f.add_subplot(2,6,5).set_ylim([-30,30])
        self.f.add_subplot(2,6,6).set_ylim([-30,30])
        self.f.add_subplot(2,6,1).plot(self.time, self.L_dot_ref[:,0], self.time, self.L_dot[:,0])
        self.f.add_subplot(2,6,2).plot(self.time, self.L_dot_ref[:,1], self.time, self.L_dot[:,1])
        self.f.add_subplot(2,6,3).plot(self.time, self.L_dot_ref[:,2], self.time, self.L_dot[:,2])
        self.f.add_subplot(2,6,4).plot(self.time, self.L_dot_ref[:,3], self.time, self.L_dot[:,3])
        self.f.add_subplot(2,6,5).plot(self.time, self.L_dot_ref[:,4], self.time, self.L_dot[:,4])
        self.f.add_subplot(2,6,6).plot(self.time, self.L_dot_ref[:,5], self.time, self.L_dot[:,5])
        
        self.f.add_subplot(2,6,7).set_ylim([450,750])
        self.f.add_subplot(2,6,8).set_ylim([450,750])
        self.f.add_subplot(2,6,9).set_ylim([450,750])
        self.f.add_subplot(2,6,10).set_ylim([450,750])
        self.f.add_subplot(2,6,11).set_ylim([450,750])
        self.f.add_subplot(2,6,12).set_ylim([450,750])
        self.f.add_subplot(2,6,7).plot(self.time, self.L_ref[:,0], self.time, self.L[:,0])
        self.f.add_subplot(2,6,8).plot(self.time, self.L_ref[:,1], self.time, self.L[:,1])
        self.f.add_subplot(2,6,9).plot(self.time, self.L_ref[:,2], self.time, self.L[:,2])
        self.f.add_subplot(2,6,10).plot(self.time, self.L_ref[:,3], self.time, self.L[:,3])
        self.f.add_subplot(2,6,11).plot(self.time, self.L_ref[:,4], self.time, self.L[:,4])
        self.f.add_subplot(2,6,12).plot(self.time, self.L_ref[:,5], self.time, self.L[:,5])

    def onExec(self):
        self.resetData()
        self.control()
        self.draw()
        self.canvas.draw()

    def control(self):
        self.L_dot = np.zeros([1,6])
        self.L_dot_ref = self.L_dot
        
#        self.L = np.array([[597.010, 597.010, 597.010, 597.010, 597.010, 597.010]])
        self.L = np.array([[float(self.lastText[0]),float(self.lastText[1]),float(self.lastText[2]),float(self.lastText[3]),float(self.lastText[4]),float(self.lastText[5])]])
        self.L_ref = self.L
                       
        # position and velocity goals
        #L_goal = np.ones(6) * 597.018
#        self.L_goal = np.array([594.41, 597.16, 594.44, 601.93, 602.65, 592.40])
        #L_dot_goal = np.ones(6) * 9.063
#        self.L_dot_goal = np.array([-0.920, 0.05, -0.910, 1.74, 1.99, -1.63])

        self.L_goal = np.array([float(self.extractL1()), float(self.extractL2()), float(self.extractL3()), float(self.extractL4()), float(self.extractL5()), float(self.extractL6())])
        self.L_dot_goal = np.array([float(self.extractL1Dot()), float(self.extractL2Dot()), float(self.extractL3Dot()), float(self.extractL4Dot()), float(self.extractL5Dot()), float(self.extractL6Dot())])
        
        self.L_delta = self.L_goal - self.L[-1,:]
        
        # error initialization
        self.error_L_dot_last = np.zeros(6)
        self.error_L_dot = self.L_dot_ref[0,:] - self.L_dot[0,:]
        self.error_L = self.L_ref[0,:] - self.L[0,:]
        
        self.int_L_dot = 0
        self.dif_L_dot = 0
        
        self.time = np.zeros(1)
        self.time_rise = 0.1
        self.time_delay = 0.1
        self.time_goal_array = np.zeros(6)
        if (abs(self.L_dot_goal[0]) > 0):
            print(abs(self.L_delta[0] / self.L_dot_goal[0]))
            self.time_goal = self.extractT()
        else:
            self.time_goal = self.time_delay
        
        self.n_rise = int(self.time_rise / self.dt)
        self.n_goal = int(self.time_goal / self.dt)

        for self.n in range(0, self.n_goal + self.n_rise):
            # sensor acquisition here

            # motion planning velocity
            rising = np.ones(6) * (self.n / float(self.n_rise))
            falling = np.ones(6) * ((self.n - self.n_goal) / float(self.n_rise))
                
            if (self.n < self.n_rise):
                self.L_dot_ref = np.append(self.L_dot_ref, self.L_dot_goal * rising[None,:], axis=0)
            elif (self.n < self.n_goal) and (self.n >= self.n_rise):
                self.L_dot_ref = np.append(self.L_dot_ref, self.L_dot_goal[None,:], axis=0)
            elif (self.n < self.n_goal + self.n_rise) and (self.n >= self.n_goal):
                self.L_dot_ref = np.append(self.L_dot_ref, - self.L_dot_goal * falling[None,:] + self.L_dot_goal, axis=0)
            elif (self.n > self.n_goal):
                self.L_dot_ref = np.append(self.L_dot_ref, np.zeros(6))
            
            # motion planning position
            self.data_L_ref = self.L_ref[self.n,:] + (self.L_dot_ref[self.n,:] * self.dt)
            self.L_ref = np.append(self.L_ref, self.data_L_ref[None,:], axis=0)

            # error L calculation
            self.error_L = self.L_ref[self.n,:] - self.L[self.n,:]

            # output PID L
            if (self.n % 10 == 0):
                self.PID_L = self.KP_L * self.error_L
            
            # error L dot calculation
            self.error_L_dot = self.L_dot_ref[self.n,:] - self.L_dot[self.n,:] + self.PID_L
            self.int_L_dot += self.error_L_dot
            self.dif_L_dot = self.error_L_dot - self.error_L_dot_last
            
            # output PID L dot
            self.PID_L_dot = self.KP_L_dot * (self.error_L_dot + 1/self.TI_L_dot * self.int_L_dot + self.TD_L_dot * self.dif_L_dot)
            
            
            # plant simulation
            self.data_L_dot = (1 - (self.Bm/self.Jm) * self.dt) * self.L_dot[self.n,:] + (self.Km/self.Jm) * self.PID_L_dot * self.dt
            self.data_L = self.L[self.n,:] + self.L_dot[self.n,:] * self.dt
            
            self.L_dot =  np.append(self.L_dot, self.data_L_dot[None,:], axis=0)
            self.L = np.append(self.L, self.data_L[None,:], axis=0)
            
            # n + 1
            self.error_L_dot_last = self.error_L_dot
            self.time = np.append(self.time, self.time[self.n] + self.dt)    
			
    def onPrev(self):
        if self.line > 1.0:
            self.line -= 1.0
        else:
            self.line = 1.0

    def onNext(self):
        if self.line < self.maxLine:
            self.line += 1.0
        
    def onSave(self):
        name=tkFileDialog.asksaveasfile(mode='w',defaultextension=".spnc")
        text2save=str(self.txtNC.get(0.0,END))
        name.write(text2save)
        name.close

    def onClear(self):
        self.txtNC.delete(1.0, 'end')
        self.trajectoryG0 = np.array([[0.], [0.], [0.]])
        self.trajectoryG1 = np.array([[0.], [0.], [0.]])
        self.draw()
        self.canvas.draw()

    def onOpen(self):
        ftypes = [('Stewart Platform NC files', '*.spnc'), ('All files', '*')]
        dlg = tkFileDialog.Open(self, filetypes = ftypes)
        fl = dlg.show()

        if fl != '':
            text = self.readFile(fl)
            self.txtNC.insert(1.0, text)
            self.maxLine = math.floor(float(self.txtNC.index('end-1c')))

    def readFile(self, filename):
        f = open(filename, "r")
        text = f.read()
        return text

    def onInit(self):
        self.trajectoryG0 = np.array([[0.], [0.], [0.]])
        self.trajectoryG1 = np.array([[0.], [0.], [0.]])
        self.line = 1.0
        self.onExec()

    def onRun(self):
        self.run = not self.run
        if self.run:
            print("Robot Started")            

            #time.sleep(5)
            while self.line <= self.maxLine:
                self.onExec()
#                t = 0.
#                while t < self.travelTime:
#                    t+=0.1
                    #time.sleep(0.1)

                    # run control here
                    
                if self.line == self.maxLine:
                    self.onStop()

                if not self.run:
                    break
                #time.sleep(5)

                self.onNext()
                                
        else:
            print("Robot Paused")

    def onStop(self):
        print("Robot Stopped")
        self.run = False

    def onExit(self):
        self.quit()
        self.destroy()

    def resetData(self):
        self.txtL1.delete(1.0, 'end')
        self.txtL2.delete(1.0, 'end')
        self.txtL3.delete(1.0, 'end')
        self.txtL4.delete(1.0, 'end')
        self.txtL5.delete(1.0, 'end')
        self.txtL6.delete(1.0, 'end')
        self.txtL1Dot.delete(1.0, 'end')
        self.txtL2Dot.delete(1.0, 'end')
        self.txtL3Dot.delete(1.0, 'end')
        self.txtL4Dot.delete(1.0, 'end')
        self.txtL5Dot.delete(1.0, 'end')
        self.txtL6Dot.delete(1.0, 'end')

def main():
    root = Tk()
    myFont = tkFont.nametofont("TkDefaultFont")
    myFont.configure(size=11)
 
    run = Run(root)
    #root.attributes('-fullscreen', True)
    root.geometry('1280x729+0+0')
    root.option_add('*Font', myFont)
    root.mainloop()
    root.quit()
    root.destroy()


if __name__ == '__main__':
    main()
