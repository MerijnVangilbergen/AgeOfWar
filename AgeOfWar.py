from tkinter import *
from PIL import ImageTk, Image
import time

from pandas import read_excel
from functools import partial

class TEAM:
    def __init__(self,numOfBerries,direction,keys):
        self.experience = 0
        self.berries = numOfBerries
        self.berriesLabel = Label(window, text="")
        self.keyLabels = []

        self.smurfs = []
        self.direction = direction # +1 for moving to the right, -1 for moving to the left
        self.keys = keys

        self.era = 0
        self.castle = CASTLE(direction=self.direction)
        self.nextEra()

        self.MULTIPLYER_damage = 1
        self.MULTIPLYER_HP = 1
        self.MULTIPLYER_experience_gain = 1
    
    #Add gain if positive, subtract -gain if negative
    def addBerries(self,gain):
        self.berries = self.berries + gain
        self.berriesLabel.config(text="Berries: "+str(int(self.berries)) + "\n Experience: "+str(int(self.experience)))
        if self.direction == 1:
            self.berriesLabel.place(relx=.2,rely=.05)
        else:
            self.berriesLabel.place(relx=.8,rely=.05)
    
    #Create a new smurf, located at the initial position (outer left or outer right of the screen).
    def addSmurf(self,ii):
        newSmurf_DB = self.SmurfDatabase[ii]
        if self.berries >= newSmurf_DB.cost:
            self.addBerries(-newSmurf_DB.cost)

            if self.direction==1:
                smurfpos = 0
            else:
                smurfpos = 1
            
            newSmurf = SMURF(pos=smurfpos,
                             direction = self.direction,
                             HP = newSmurf_DB.HP * self.MULTIPLYER_HP,
                             damage = newSmurf_DB.damage * self.MULTIPLYER_damage,
                             range = newSmurf_DB.range,
                             img = newSmurf_DB.image,
                             width = newSmurf_DB.width,
                             height = newSmurf_DB.height,
                             cost = newSmurf_DB.cost)
            self.smurfs.append(newSmurf)

    def move(self,dx,limit):
        self.smurfs[0].move( min(dx, self.direction * (limit-self.smurfs[0].position)) )
        for ii in range(1,len(self.smurfs)):
            self.smurfs[ii].move( max(0, min(dx, (self.direction*self.smurfs[ii-1].position - self.smurfs[ii-1].relwidth - self.direction*self.smurfs[ii].position))) )

    def eliminateNegHP(self):
        if self.smurfs[0].HP <= 0:
            if self.direction == 1:
                travel = self.smurfs[0].position #number in range [0,1]
            else:
                travel = 1 - self.smurfs[0].position #number in range [0,1]
            self.experience += 10**travel * self.smurfs[0].cost**.5 * self.MULTIPLYER_experience_gain

            self.smurfs[0].display.destroy()
            del self.smurfs[0]

            if self.experience >= eraRequirement[self.era]:
                self.nextEra()

    def nextEra(self):
        #Remove all smurfs and reward with some berries
        for ii in range(len(self.smurfs)):
            self.addBerries(self.smurfs[ii].cost)
            self.smurfs[ii].display.destroy()
        self.smurfs = []

        self.era += 1
        self.SmurfDatabase = Initialise_smurfDatabase(self.era,self.direction)

        #Remove all keyLabels
        for ii in range(len(self.keyLabels)):
            self.keyLabels[ii].destroy()
        self.keyLabels = []

        #Create new keyLabels
        margin = .02
        Width = .08
        if self.direction==1:
            X = margin
        else:
            X = 1-margin-Width
        
        for ii in range(len(self.SmurfDatabase)):
            newlabel = Label(window, text=self.keys[ii].upper() + ': ' + str(self.SmurfDatabase[ii].cost) + '     ', image=self.SmurfDatabase[ii].buttonImage, compound='right')
            self.keyLabels.append(newlabel)
            self.keyLabels[ii].place(relx=X, rely=.05+ii*.1, relheight=.08, relwidth=Width)
        
        self.castle.HPmax = HPcastle[self.era]
        self.castle.HP = self.castle.HPmax

class CASTLE:
    def __init__(self,direction):
        self.HPmax = 1
        self.HP = self.HPmax
        self.damage_cooldown = 0
        self.display = Label(window, bg="dodger blue")
        if direction==1:
            self.position = 0
            self.display.place(relx=self.position, rely=1, relheight=self.HP/self.HPmax, relwidth=.02, anchor=SW)
        else:
            self.position = 1
            self.display.place(relx=self.position, rely=1, relheight=self.HP/self.HPmax, relwidth=.02, anchor=SE)

    def update_display(self):
        if self.position == 0:
            self.display.place(relx=self.position, rely=1, relheight=self.HP/self.HPmax, relwidth=.02, anchor=SW)
        else:
            self.display.place(relx=self.position, rely=1, relheight=self.HP/self.HPmax, relwidth=.02, anchor=SE)

    def update_colour(self):
        if self.damage_cooldown > .9:
            self.display.config(bg="red")
        else:
            self.display.config(bg="dodger blue")

class SMURF:
    def __init__(self,pos,direction,HP,damage,range,img,width,height,cost):
        self.position = pos
        self.direction = direction
        self.HP = HP
        self.damage = damage
        self.range = range
        self.width = width
        self.height = height
        self.relwidth = self.width / screenwidth
        self.relheight = self.height / screenheight
        self.cost = cost
        self.attack_cooldown = 0
        self.damage_cooldown = 0
        #display
        smurfLabel = Label(window,image=img)
        if self.direction == 1:
            smurfLabel.place(relx=self.position, rely=.75, width=self.width, height=self.height, anchor=SE)
        else:
            smurfLabel.place(relx=self.position, rely=.75, width=self.width, height=self.height, anchor=SW)
        self.display = smurfLabel

    def move(self,dx):
        self.position += dx * self.direction
        if self.direction == 1:
            self.display.place(relx=self.position, rely=.75, width=self.width, height=self.height, anchor=SE)
        else:
            self.display.place(relx=self.position, rely=.75, width=self.width, height=self.height, anchor=SW)

    def update_colour(self):
        if self.attack_cooldown > .95:
            self.display.config(bg="blue", fg="white")
        elif self.damage_cooldown > .9:
            self.display.config(bg="red", fg="red")
        else:
            self.display.config(bg="white", fg="white")


class SMURF_DATABASE:
    def __init__(self,cost,image,flipImage,size,HP,damage,range):
        self.cost = cost

        img_smurf = Image.open(image)
        if flipImage:
            img_smurf = img_smurf.transpose(Image.FLIP_LEFT_RIGHT)
        origWidth, origHeight = img_smurf.size

        rescalingFactor = (size / (origWidth * origHeight))**.5
        self.width = int(screenwidth * origWidth * rescalingFactor)
        self.height = int(screenheight * origHeight * rescalingFactor)

        img_smurf2 = img_smurf.resize((self.width,self.height))
        img_smurf2 = ImageTk.PhotoImage(img_smurf2)
        self.image = img_smurf2

        length = int(.03*screenwidth)
        rescalingFactor = length / max([origWidth,origHeight])
        newWidth = int(origWidth*rescalingFactor)
        newHeight = int(origHeight*rescalingFactor)
        img_button = img_smurf.resize((newWidth,newHeight))
        img_button = ImageTk.PhotoImage(img_button)
        self.buttonImage = img_button

        self.HP = HP
        self.damage = damage
        self.range = range
        
def Initialise_smurfDatabase(era, teamdirection):
    SmurfDatabase = []
    SmurfData = read_excel('SmurfData.xlsx', sheet_name="Sheet1")
    for ii in range(len(SmurfData)):
        if SmurfData['Era'][ii] == era:
            new_smurf = SMURF_DATABASE(cost = SmurfData['Cost'][ii],
                                       image = SmurfData["Image"][ii],
                                       flipImage = (SmurfData["ImageDirection"][ii] != teamdirection),
                                       size = SmurfData['Size'][ii],
                                       HP = SmurfData['HP'][ii],
                                       damage = SmurfData['Damage'][ii],
                                       range = SmurfData['Range'][ii])
            SmurfDatabase.append(new_smurf)
    return SmurfDatabase

def attack(attackers, target):
    for attacker in attackers.smurfs:
        if attacker.attack_cooldown <= 0 and abs(attacker.position - target.position) <= attacker.range:
            if attacker.direction==1:
                posmultiplyer = (1-attacker.position**2/2)
            else:
                posmultiplyer = (1-(1-attacker.position)**2/2)
            actualDamage = attacker.damage * posmultiplyer
            target.HP -= actualDamage
            target.damage_cooldown = minmod(target.damage_cooldown+1)
            attacker.attack_cooldown = minmod(attacker.attack_cooldown+1)
            if target.__class__.__name__=='CASTLE':
                target.update_display()
                attackers.experience += actualDamage * attackers.MULTIPLYER_experience_gain

def key_press(e):
    for ii in range(len(Blue.keys)):
        if e.char==Blue.keys[ii]:
            Blue.addSmurf(ii)
            break #Leave for loop if condition satisfied
    for ii in range(len(Red.keys)):
        if e.char==Red.keys[ii]:
            Red.addSmurf(ii)
            break #Leave for loop if condition satisfied
    #if e.char==' ':

def minmod(x):
    return min(1,max(0,x))

#Define parameters
fps = 16 #[frames per second]
speed = .1 #smurf speed [screen widths per second]
berries_start = 1000
berriesPerSecond = 20
eraRequirement = list([0,10000,20000,30000,float('inf')])
HPcastle = list([1,140,160,180,200])

dt_default = 1/fps #Time step between two frames [s]
dt = dt_default
dx = speed * dt #space step [screen widths]
berries_gain = berriesPerSecond * dt #money gained per time step


#Create a window
window = Tk()
window.title("Age Of War")
#get width & height of screen
#screenwidth= window.winfo_screenwidth()
#screenheight= window.winfo_screenheight()
screenwidth= 1920
screenheight= 1010
#set screensize as fullscreen and not resizable
window.geometry("%dx%d" % (screenwidth, screenheight))
window.resizable(False, False)
#Create background
backgroundImg = Image.open("background2.png")
backgroundImg = backgroundImg.resize((screenwidth,screenheight))
backgroundImg = ImageTk.PhotoImage(backgroundImg)
background = Label(window,image=backgroundImg)
background.place(relx=0, rely=0, relwidth=1, relheight=1)


#Initialize both teams with no smurfs
Blue = TEAM(numOfBerries=berries_start, direction=+1, keys=['q','s','d','f'])
Red = TEAM(numOfBerries=berries_start, direction=-1, keys=['j','k','l','m'])


#Create control window
controlwindow = Tk()
controlwindow.title("Control window")
#set screensize as fullscreen and not resizable
controlwindow.geometry("%dx%d" % (screenwidth, screenheight))


VERT_SEPARATION = .1
RELY = VERT_SEPARATION

def BUTTONaddBerriesBlue():
    Blue.addBerries(500)
def BUTTONaddBerriesRed():
    Red.addBerries(500)
Button(controlwindow, text='Add 500 berries', command=BUTTONaddBerriesBlue).place(relx=.1,rely=RELY,anchor=NW)
Button(controlwindow, text='Add 500 berries', command=BUTTONaddBerriesRed).place(relx=.9,rely=RELY,anchor=NE)


RELY += VERT_SEPARATION
def BUTTONboostDamageBlue():
    Blue.MULTIPLYER_damage = Blue.MULTIPLYER_damage*1.1
def BUTTONboostDamageRed():
    Red.MULTIPLYER_damage = Red.MULTIPLYER_damage*1.1
Button(controlwindow, text='Boost damage by 10%', command=BUTTONboostDamageBlue).place(relx=.1,rely=RELY,anchor=NW)
Button(controlwindow, text='Boost damage by 10%', command=BUTTONboostDamageRed).place(relx=.9,rely=RELY,anchor=NE)

def BUTTONresetDamageBlue():
    Blue.MULTIPLYER_damage = 1
def BUTTONresetDamageRed():
    Red.MULTIPLYER_damage = 1
Button(controlwindow, text='Reset damage boost', command=BUTTONresetDamageBlue).place(relx=.3,rely=RELY,anchor=NW)
Button(controlwindow, text='Reset damage boost', command=BUTTONresetDamageRed).place(relx=.7,rely=RELY,anchor=NE)


RELY += VERT_SEPARATION
def BUTTONboostHPBlue():
    Blue.MULTIPLYER_HP = Blue.MULTIPLYER_HP*1.1
def BUTTONboostHPRed():
    Red.MULTIPLYER_HP = Red.MULTIPLYER_HP*1.1
Button(controlwindow, text='Increase HP by 10%', command=BUTTONboostHPBlue).place(relx=.1,rely=RELY,anchor=NW)
Button(controlwindow, text='Increase HP by 10%', command=BUTTONboostHPRed).place(relx=.9,rely=RELY,anchor=NE)

def BUTTONresetHPBlue():
    Blue.MULTIPLYER_HP = 1
def BUTTONresetHPRed():
    Red.MULTIPLYER_HP = 1
Button(controlwindow, text='Reset HP', command=BUTTONresetHPBlue).place(relx=.3,rely=RELY,anchor=NW)
Button(controlwindow, text='Reset HP', command=BUTTONresetHPRed).place(relx=.7,rely=RELY,anchor=NE)


RELY += VERT_SEPARATION
def BUTTONboostExperienceGainBlue():
    Blue.MULTIPLYER_experience_gain = Blue.MULTIPLYER_experience_gain*1.1
def BUTTONboostExperienceGainRed():
    Red.MULTIPLYER_experience_gain = Red.MULTIPLYER_experience_gain*1.1
Button(controlwindow, text='Boost experience gain by 10%', command=BUTTONboostExperienceGainBlue).place(relx=.1,rely=RELY,anchor=NW)
Button(controlwindow, text='Boost experience gain by 10%', command=BUTTONboostExperienceGainRed).place(relx=.9,rely=RELY,anchor=NE)

def BUTTONresetDamageBlue():
    Blue.MULTIPLYER_experience_gain = 1
def BUTTONresetDamageRed():
    Red.MULTIPLYER_experience_gain = 1
Button(controlwindow, text='Reset damage boost', command=BUTTONresetDamageBlue).place(relx=.3,rely=RELY,anchor=NW)
Button(controlwindow, text='Reset damage boost', command=BUTTONresetDamageRed).place(relx=.7,rely=RELY,anchor=NE)


#Add KeyPress actions
window.bind('<KeyPress>',key_press)
controlwindow.bind('<KeyPress>',key_press)

#Start game
while Blue.castle.HP > 0 and Red.castle.HP > 0:
    start_time = time.time()

    # Add Berries
    Blue.addBerries(berries_gain)
    Red.addBerries(berries_gain)

    # Attack
    for smurf in Blue.smurfs:
        smurf.attack_cooldown = minmod(smurf.attack_cooldown-dt)
        smurf.damage_cooldown = minmod(smurf.damage_cooldown-dt)
    for smurf in Red.smurfs:
        smurf.attack_cooldown = minmod(smurf.attack_cooldown-dt)
        smurf.damage_cooldown = minmod(smurf.damage_cooldown-dt)
    Blue.castle.damage_cooldown = minmod(Blue.castle.damage_cooldown-dt)
    Red.castle.damage_cooldown = minmod(Red.castle.damage_cooldown-dt)

    if Blue.smurfs!=[] and Red.smurfs!=[]:
        attack(attackers=Blue, target=Red.smurfs[0])
        attack(attackers=Red, target=Blue.smurfs[0])
        Blue.eliminateNegHP()
        Red.eliminateNegHP()
    elif Blue.smurfs!=[]:
        attack(attackers=Blue, target=Red.castle)
    elif Red.smurfs!=[]:
        attack(attackers=Red, target=Blue.castle)
    
    # Change label colours
    for ii in range(len(Blue.smurfs)):
        Blue.smurfs[ii].update_colour()
    for ii in range(len(Red.smurfs)):
        Red.smurfs[ii].update_colour()
    Blue.castle.update_colour()
    Red.castle.update_colour()

    # Move
    if Blue.smurfs!=[] and Red.smurfs!=[]:
        limit = (Red.smurfs[0].position + Blue.smurfs[0].position)/2
        Blue.move(dx,limit)
        Red.move(dx,limit)
    elif Blue.smurfs!=[]:
        limit = 1
        Blue.move(dx,limit)
    elif Red.smurfs!=[]:
        limit = 0
        Red.move(dx,limit)

    window.update()

    end_time = time.time()
    time.sleep(max(0,dt-(end_time-start_time)))

window.mainloop()