# HPC viz
# adds squares based on list values to the pictograph upon starting
# adds circles using a yaml file
# updates the circles w a log in the form of a dictionary
# reads in files to display text in the leftmost panel and the bottom banner
# left panel allows manual scrolling, bottom banner "scrolls" automatically
# also download: colorfriendlyviz.kv, melete.rst,  users.rst, and jobs.yaml

from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics','height', '700')
Config.set('graphics','resizable', '0') #set to 1 to allow resizing
    
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Rotate, Ellipse
from kivy.animation import *
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.clock import Clock
from kivy.properties import ListProperty

from random import randint
import webbrowser
import yaml

class SpecsPanel(BoxLayout):
    pass

class Square(Widget):
    color = ListProperty([0,0,0,1])

class Pictograph(BoxLayout):

    nodesList = ListProperty([[], [], []])
    nodesCount = ListProperty([9,3,15])
    colList = ["freeCol","blockedCol","busyCol"]
    clr = [[.4,.67,.33,1],[1,.93,.2,1],[.93,.2,.2,1]]
    
    def addNodes(self, dt):
        for a in range(len(self.nodesCount)):
            if len(self.nodesList[a]) < self.nodesCount[a]:
                anim = Animation(x=42,
                                 y=((len(self.nodesList[a])+1)*21),
                                 t="out_bounce",
                                 d=2)
                s=Square(pos=(42,800),
                         color=self.clr[a])
                self.nodesList[a].append(s)
                anim.start(s)
                self.ids[self.colList[a]].add_widget(s)

    def fewerNodes(self,b):
        self.nodesCount[b] = self.nodesCount[b]-1
        self.ids[self.colList[b]].remove_widget(self.nodesList[b][self.nodesCount[b]])
        return(self.nodesList[b].pop())

    def moreNodes(self, dt):
        a=randint(0,2)
        if a==0:
            c=2
        elif a==1:
            if len(self.nodesList[0])==0:
                a=1
                c=2
            else:
                c=0
        else:
            if len(self.nodesList[1])==0:
                c=0
            else:
                c=1
        b=self.fewerNodes(c)
        b=Square(color=self.clr[a],
                 pos=(42,1000))
        self.nodesList[a].append(b)
        self.nodesCount[a]=self.nodesCount[a]+1
        anim = Animation(x=42,
                         y=((len(self.nodesList[a]))*21),
                         t="out_bounce",
                         d=2)
        anim.start(b)
        self.ids[self.colList[a]].add_widget(b)

class Circle(Button):
    color = ListProperty([0,0,0,1])

    def details(self,i):
        key={"S":"Science","T":"Technology","E":"Engineering","M":"Math", \
             "R":"Running","Q":"Queued"}

        hr=int((370-i["time"])//60)
        m=int((370-i["time"])%60)
        t=""
        if hr>0:
            t=str(hr)+" hour"
            if hr>1:
                t=t+"s"
        if m>0:
            if len(t)>0:
                t=t+" and "
            t=t+str(m)+" minute"
            if m>1:
                t=t+"s"
        if i["time"] < 123:
            tColor='[color=EDF392]'
        elif i["time"] >= 123 and i["time"] < 246:
            tColor='[color=F3C663]'
        else:
            tColor='[color=F3CA35]'
        t=tColor+t+'[/color]'
        
        
        if i["status"] == "R":
            line2 = "\n- Expected to finish in " + t
        else:
            if .5 <= i["priority"] and i["priority"] < .67:
                line2 = "\n- [color=EDF392]Low priority " + '[/color]' + "(" + str((1.1-i["priority"])*63740) + ")"
            elif .67 <= i["priority"] and i["priority"] < .84:
                line2 = "\n- [color=F3C663]Medium priority " +'[/color]' + "(" + str((1.1-i["priority"])*63740) + ")"
            else:
                line2 = "\n- [color=F3CA35]High priority " + '[/color]' + "(" + str((1.1-i["priority"])*63740) + ")"

        description=("- " + str(key[str(i["status"])]) + " on queue: " + str(i["queue"]) + \
           line2 + "\n- Using " + str(i["nodes"]) + " nodes" + \
           "\n- " + str(key[str(i["stem"])]) + " job " + "submitted by " + \
           '[color=8B33B4]' + str(i["user"]) + '[/color]')
        
        popup = Popup(title="Job ID: " + str(i["id"]),
                      title_font="Geneva.dfont",
                      title_size=30,
                      size_hint=(None,None),
                      size=(500,250),
                      content=Label(text=description,
                                    markup=True,
                                    font_size=20,
                                    font_name="Geneva.dfont",
                                    pos=self.pos))
        popup.open()

class BalloonRace(BoxLayout):

    f = yaml.load(open("jobs.yaml"))
    log = {"q1":{},"q2":{},"q3":{}}
                
    def addJobs(self, dt):

        for queue in self.f.keys():
            for job in self.f[queue]:
                xPos = randint(10,75)
                anim = Animation(x=xPos,
                                 y=(self.f[queue][job]["time"]),
                                 t="out_back",
                                 d=3)
                p=self.f[queue][job]["priority"]
                p=.75
                stemClr = {"S":(.6,.13,.53,p), "T":(.07,.67,.6,p), \
                           "E":(1,.93,.2,p), "M":(.93,.2,.2,p)}
                c = Circle(id=str(self.f[queue][job]["id"]),
                           color=stemClr[(self.f[queue][job]["stem"])],
                           pos=(xPos,0),
                           size_hint=(None, None),
                           size=(self.f[queue][job]["nodes"], self.f[queue][job]["nodes"]))
                c.info={}
                for detail in self.f[queue][job]:
                    c.info[detail]=self.f[queue][job][detail]
                anim.start(c)
                self.ids[self.f[queue][job]["queue"]].add_widget(c)
                self.log[self.f[queue][job]["queue"]].update({str(c.id):c})
          
    def progress(self, dt):
        
        for queue in self.f.keys():
            for job in self.f[queue]:
                c=self.log[self.f[queue][job]["queue"]][str(self.f[queue][job]["id"])]
                t=(randint(6,10))*.6
                if c.y < 900:
                    if self.f[queue][job]["status"]=="R": #moves active jobs
                        a=.07
                    else: #moves queued jobs
                        a=.1
                    a=(randint(0,10))*a
                    initialY = self.f[queue][job]["time"]
                    if initialY > 5:
                        self.f[queue][job]["status"]="R"
                    self.f[queue][job]["time"] = initialY + initialY*a
                    if self.f[queue][job]["time"] > 370:
                        self.f[queue][job]["time"] = 900
                    anim = Animation(x=c.x,
                                     y=self.f[queue][job]["time"],
                                     t="out_back",
                                     d=t)
                    #c.pos
                    self.log[self.f[queue][job]["queue"]][str(self.f[queue][job]["id"])].pos = (c.x,initialY)
                    anim.start(self.log[self.f[queue][job]["queue"]][str(self.f[queue][job]["id"])])

                    c.info["time"]=self.f[queue][job]["time"]
                    c.info["status"]=self.f[queue][job]["status"]
                else:
                    self.f[queue][job]["time"] = 3
                    self.f[queue][job]["status"]="Q"
                    restart=Animation(x=c.x,
                                      y=self.f[queue][job]["time"],
                                      d=t)
                    self.log[self.f[queue][job]["queue"]][str(self.f[queue][job]["id"])].pos = (c.x,0)
                    restart.start(self.log[self.f[queue][job]["queue"]][str(self.f[queue][job]["id"])])

                    c.info["time"]=self.f[queue][job]["time"]
                    c.info["status"]=self.f[queue][job]["status"]


                    
class ClusterDetailsScreen(Screen):

    def importText(self,fileName):
        file=open(fileName,"r")
        return(file.read())

    def link(instance,value):
        webbrowser.open(value)


class Comment(Bubble):

    def __init__(self,t,p,s,a,**kwargs):
        super(Comment,self).__init__(**kwargs)
        self.t=t
        self.p=p
        self.s=s
        self.a=a

##        if self.a=='left_top' or 'left_mid' or 'left_bottom' or \
##           'right_top' or'right_mid' or'right_bottom':
##            self.bp=(self.p[0]+4,self.p[1])
##        else:
##            self.bp=(self.p[0],self.p[1]+20)
        
        self.arrow_pos=self.a
        self.size_hint=(None,None)
        self.size=self.s
        self.pos=self.p
        self.background_image='whitebg.png'
        self.background_color=(.4,.96,.93,1)
        
        self.l=Label(text=self.t,
                     color=(0,0,0,1),
                     pos=self.p,
                     size_hint=(None,None),
                     size=self.s,
                     font_size=18,
                     font_name='Geneva.dfont',
                     halign='center')

##        with self.l.canvas.before:
##            Rectangle(color=(.78,.99,.98,1),
##                      size=(self.s[0]-8,self.s[1]-8),
##                      pos=(self.p[0]+4,self.p[1]+4))
        
 #           Color=(.78,.99,.98,1)
#(.4,.96,.93,1)

        self.add_widget(self.l)
        self.opacity=0

    def appear(self,dt):
        self.opacity=0
        self.animate=Animation(opacity=1, duration=1) + \
                      Animation(opacity=1,duration=10) + \
                      Animation(opacity=0,duration=1)
        self.animate.start(self)

class ColorFriendlyViz(App):

    def scrollBanner(self,dt):
        SM.ids['banner'].pos=(2000,0)
        anim = Animation(x=(0-(self.charCount()*20)),
                         y=(0),
                         d=60)     
        anim.start(SM.ids['banner'])

    def charCount(self):
        count=0
        markUp=False
        f=open("users.rst")
        for line in f:
            for word in line:
                for char in word:
                    if char=="[":
                        markUp=True
                    elif char=="]":
                        markUp=False
                    elif markUp==False:
                        count+=1
        print(count)
        return(count)

        
    def build(self):
##        SM = ScreenManager(transition=NoTransition())
##        SM.add_widget(ClusterDetailsScreen(name='cluster details'))
        global SM
        window=RelativeLayout()
        SM = ClusterDetailsScreen()
        window.add_widget(SM)
        picto = SM.ids['pictoPanel']
        bubble = SM.ids['bubblePanel']
        specs = SM.ids['specsPanel']

#'left_top', 'left_mid', 'left_bottom',
#'top_left', 'top_mid', 'top_right',
#'right_top', 'right_mid', 'right_bottom',
#'bottom_left', 'bottom_mid', 'bottom_right'
        
        c1=Comment("capabilities of\nthe cluster in\nlayman's terms", \
                   (10,100),(152,89),'top_mid')
        c2=Comment("adequate size +\nuniform strokes =\nreadable font", \
                   (20,390),(175,90),'bottom_left')
        c3=Comment("1 square falling into \nplace = 4 nodes\nchanging status", \
                   (150,230),(207,80),'right_bottom')
        c4=Comment("1 circle = 1 job with\ndiameter, position, color,\nand transparency\nreflecting job\ncharacteristics", \
                   (420,200),(245,120),'right_bottom')
        c5=Comment("The circles rise like\nbubbles as they\napproach completion,\nfinally floating away\nwhen they finish.", \
                   (690,360),(198,140),'bottom_left')
        c6=Comment("scrolling banner with\nhyperlinks that direct\nto the user's website", \
                   (100,10),(230,80),'right_bottom')
        c7=Comment("Bar graphs depict\ndifferences more\nclearly than pie\n charts[2].", \
                   (210,500),(170,110),'bottom_right')
        c8=Comment("Click on a circle\nto see job details.", \
                   (710,230),(180,60),'left_mid')
        c9=Comment("color-blind-\nfriendly palette", \
                   (420,450),(160,60),'right_bottom')

        comments=[c1,c2,c3,c4,c5,c6,c7,c8,c9]

        for x in comments:
            window.add_widget(x)
        
        specs.ids['details'].text = SM.importText('melete.rst')
        SM.ids['banner'].text = SM.importText('users.rst')

        Clock.schedule_once(self.scrollBanner)
##        Clock.schedule_once(c1.appear,12)
##        Clock.schedule_once(c2.appear,24)
##        Clock.schedule_once(c3.appear,36)
##        Clock.schedule_once(c4.appear,48)
##        Clock.schedule_once(c5.appear,60)
##        Clock.schedule_once(c6.appear,72)
##        Clock.schedule_once(c7.appear,84)
##        Clock.schedule_once(c8.appear,96)
##        Clock.schedule_once(c9.appear,108)
        Clock.schedule_interval(self.scrollBanner, 60)
        Clock.schedule_interval(picto.addNodes, .1)
        Clock.schedule_interval(picto.moreNodes, 5)
        Clock.schedule_once(bubble.addJobs)
        Clock.schedule_interval(bubble.progress, 6.1)
        
        return window


if __name__ == "__main__":
    ColorFriendlyViz().run()
    

