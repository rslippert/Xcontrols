import sys
import pygame
from pygame import gfxdraw
from pygame.locals import *
import time
import math
from screeninfo import get_monitors
from functools import *

# Define some stuff
WHITE = (255,255,255)
XBLACK = (0,0,0)
BLUE = (70,210,255)
LTBLUE = (73,204,255)
RED = (255,70,70)
YELLOW = (255,245,64)
PURPLE = (255,130,255)
GRAY = (116,116,11)
GREY_B = (111, 111, 111)
GREEN = (70,255,70)
COLS_DEF= [GREEN,BLUE,PURPLE,GRAY,YELLOW]
GREEN_HI= (155, 255, 155)

button_flag={ }  # The named mouse button state flags dictionary
                 # button cap names all have pressed states here
parameter={}

#define the control types
XX=0  #xarg['pos'] for x
YY=1  #xarg['pos'] for y
MM=0
BB=1
last_mouse = False #turned on by mouse events, off by update
mevent=[]
#-------------------------------------------------------------------------------
def process_text( the_text ):
    print('text=',the_text)
#---------------------------------------------------------------------------
def process_keyboard(  command ):
    print('keyboard event ',command)
    return( True)
#---------------------------------------------------------------------------
def key_event( event):
    process_keyboard( event.unicode )
#---------------------------------------------------------------------------
class TextOut:
    def __init__(self, screen):
        self.font=pygame.font.Font(pygame.font.get_default_font(), 20)
        self.fontsize = self.font.size("0")
        self.width = self.fontsize[0]
        self.height = self.fontsize[1]
        self.setxy(10,10)
        self.screen=screen
    def tprint(self, textString, color):
        textBitmap = self.font.render(textString, True, color)
        self.screen.blit(textBitmap, (self.x, self.y))
        self.y += self.height
    def text_pix(self, txt): # get a text area size
        return( self.font.size(txt) )
    def indent(self):
        self.x += self.width*4
    def place(self, x,y,text, color):
        self.setxy(x,y)
        self.tprint( text, color)
    def unindent(self):
        self.x -= self.width*4
    def setxy(self, x, y):
        self.x = x
        self.y = y

#--- get control xobj args , name, xtype, number etc. ----------------
def xobj_args( name, xtype, src, pos ): # return args for a control object
        return{
                'xtype': xtype, # xtype of control object
                'src' : src,    # source number/name of object can be multiple
                'data':{},      #data refs for SET_DATA
                'action':{},    #actions refs for SET_ACTION
                'num2' : 0,     #second axis or grouped button
                'pos':  pos,    # xobj x,y screen pos
                'lab_top': '',  # label, pos: 'top','bot','right','left','not'
                'lab_bot': '',  # label, pos: 'top','bot','right','left','not'
                'value':  [0,0,0],   # value object
                'lastval': 0,    # prior accessed value
                'rate':  9999999, # update rate
                'trans': [[-1,0,1],[-1,0,1]],  # input list to output list trans
                'last_time': time.time(),   #time since last update
                'm_num': [26,27,28], # multi sw numbers
                'display': False, # whether to display or not
                'is_widget' : False, # widget class requires extra stuff
                'source': False     # default to self is not the source
                }
#---------------------------------------------------------------------------
sim_tics=0
def process_sim( time_rate ):
    global sim_tics
    sim_tics += 1
    if sim_tics<time_rate:
        return()
    # process the simulation

#---------------------------------------------------------------------------
def places( number, nplace ): # truncate number to nplace digits
    nm = int(number *1000000) #convert to integer
    digits = len(str(nm)) # number of digits
    nm = float(int(nm/10**(digits-nplace))*10**(digits-nplace))/1000000
    if nm >= 100:
        return(int(nm))
    return( nm )
#--------------------------------------------------------------------------
def drange( x,y,inc): # return a float range list, last value inclusive
    lst=[x]
    xx = x+inc
    while xx<=y:
        lst.append( xx)
        xx += inc
    return(lst)
#---------------------------------------------------------------------------
class Xcontrol:
    def __init__( self, caption, screen, JOY):
        self.xctls={} # library for control objects
        self.caption=caption
        self.clock = pygame.time.Clock() # Used for how fast screen updates
        self.time=time.time()            #current time from start
        self.font = pygame.font.Font(None, 25)
        self.info = {}  #dictionary of accilary information
        self.info['monitors']=get_monitors()
        self.txt = TextOut( screen)  # create screen text writing object
        self.screen = screen
        self.JOY = JOY  #True is joystick is available for use
        self.version = .05

#---------------------------------------------------------------------------
    def mouse_event(self, event, pos):
        #buttons: 1=left 2=middle 3=right 4=scrollup 5=scrolldwon pos[0] is x
        last_mouse = True
        keys = self.xctls.keys()
        for name in keys:
            xarg = self.xctls[name]
            if xarg['xtype']=='MOUSEB':
                touches=xarg['touches']
                args = xarg['args']
                self.process_mouse_buttons( touches, args, event, pos)
            elif xarg['xtype']=='BSW' or xarg['xtype']=='SW2':
                touches=xarg['touches']
                self.process_mouse_BSW( xarg, touches, pos)
    #---------------------------------------------------------------------------
    def mouse_event_wh(self, event, pos):
        last_mouse = True
        keys = self.xctls.keys()
        for name in keys:
            xarg = self.xctls[name]
            if  xarg['xtype']=='MAXIS':
                self.process_mouse_maxis( xarg, event.dict['y'], pos)
    #---------------------------------------------------------------------------
    def mouse_event_txin(self, event, pos):
        keys = self.xctls.keys()
        for name in keys:
            xarg = self.xctls[name]
            if  xarg['xtype']=='TXIN':
                xx,yy = xarg['pos']
                input_rect = xarg['rect']
                if input_rect.collidepoint(event.pos):
                    xarg['active'] = True
                else:
                    xarg['active'] = False
    #---------------------------------------------------------------------------
    def mouse_event_txkey(self, event):
        keys = self.xctls.keys()
        for name in keys:
            xarg = self.xctls[name]
            if  xarg['xtype']=='TXIN' and xarg['active']:
                if event.key == pygame.K_BACKSPACE:
                    arg['value'][0] = arg['value'][0][:-1]
                elif event.key<13 or event.key==27:
                    pass # ignore control characters
                else:
                    leng = len(event.unicode)
                    if leng==0:
                        ichar=0
                    else:
                        ichar = ord(event.unicode)
                    if event.key==13:
                        process_text( xarg['value'][0] )
                        xarg['value'][0] = ''
                    elif leng==0 or ichar<28 or ichar==127:
                        pass
                    elif event.mod==0 or event.mod==1 \
                         or event.mod==2 or event.mod==4096:
                        #print('TXIN event.mod=',event.mod)
                        xarg['value'][0] += event.unicode
                return(True)
        return(False)
    #---------------------------------------------------------------------------
    def build_mouseBSW(self, pos):
        xx,yy=pos
        item = [pygame.Rect(xx-18, yy-20, 36, 40), False]
        return( item )
    #---------------------------------------------------------------------------
    def build_mouseButns(self, num, col, colh, set_radio, pos):
        touches=[]
        caption=''
        xx,yy=pos
        args={'radio': set_radio }
        if num<0: # neg so arrange -num of buttons across the screen
            for i in range(0,-num):
                xpos = xx+i*110
                item = [pygame.Rect(xpos, yy, 100, 35), False, col, colh, caption]
                touches.append( item)
        else: # arrange num buttons down the screen
            for i in range(0,num):
                ypos = yy+i*65
                item = [pygame.Rect(xx, ypos, 100, 35), False, col, colh, caption]
                touches.append( item)
        return([touches, args])
#---------------------------------------------------------------------------
    def process_mouse_buttons( self, touches, args, event, pos):
        #buttons: 1=left 2=middle 3=right 4=scrollup 5=scrolldwon pos[0] is x
        last_mouse = True
        # process mouse/touch buttons
        for i, item in enumerate(touches):
            rect,pressed,color,colorh,cap = item
            if rect.collidepoint(pos):
                if pressed: # cycle off the button
                    touches[i][1] = False  # turn off pressed value
                else: # turn on and radio if needed
                    touches[i][1] = True
                    if args['radio'] :
                        for j in range(0,len(touches)):
                            if j != i:
                                touches[j][1] = False
    #---------------------------------------------------------------------------
    def process_mouse_BSW( self, xarg, touches, pos):
        rect,pressed = touches
        if rect.collidepoint(pos):
            if True:  #was pressed: # cycle off the button
                if xarg['value'][0]:
                    xarg['value'][0]=False # switching off
                else:
                    xarg['value'][0] = True # switching on
    #---------------------------------------------------------------------------
    def process_mouse_maxis( self, xarg, y, pos):
        xx,yy = xarg['pos']
        rect = pygame.Rect(xx-60, yy-60, 120, 120)
        if rect.collidepoint(pos):
            xarg['value'][0] += y * xarg['rate']
#------------------------------------------------------------------------------
    def pos(self, name, x,y):
        self.xctls[name]['pos'] = [x,y]
#------------------------------------------------------------------------------
    def setval(self, name, val):
        xarg = self.xctls[name]
        xarg['value'][0] = val
        if xarg['xtype']=='SLIDER_Y':
            perc = (val-xarg['min']) /  (xarg['max'] - xarg['min'])
            dim = xarg['shape'][1]+6
            self.xctls[name]['slidPos']=perc*dim
        elif xarg['xtype']=='SLIDER_X':
            perc = (val-xarg['min']) /  (xarg['max'] - xarg['min'])
            dim = xarg['shape'][0]+6
            self.xctls[name]['slidPos']=perc*dim
#------------------------------------------------------------------------------
    def getval(self, name):
        if self.xctls[name]['is_widget']:
            self.xctls[name]['value'][0] = self.xctls[name]['widget'].value
            return(self.xctls[name]['widget'].value )
        else:
            return(self.xctls[name]['value'][0] )

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
    def colors( self, name,  value):
        self.xctls[name][ 'color']=value
#-------------------------------------------------------------------------------
    def label_top( self, name,  value):
        self.xctls[name][ 'lab_top']=value
#-------------------------------------------------------------------------------
    def rate( self, name,  rate):
        self.xctls[name][ 'rate']=rate
#-------------------------------------------------------------------------------
    def label_bot( self, name,  value):
        self.xctls[name][ 'lab_bot']=value
#-------------------------------------------------------------------------------
    def setcap(self, cap):
        self.caption = cap
#-------------------------------------------------------------------------------
    def sw_caps(self, cap1, cap2):
        self.caption = cap1
        self.cap2 = cap2
#-------------------------------------------------------------------------------
    def grid(self, name, grid):
        self.xctls[name][ 'grid']=grid
        if self.xctls[name]['xtype']=='SLIDER_Y':
            self.xctls[name]['min']= grid[0]
            self.xctls[name]['max'] = grid[1]
            self.xctls[name]['step']= grid[2]
        elif self.xctls[name]['xtype']=='SLIDER_X':
            self.xctls[name]['min']= grid[0]
            self.xctls[name]['max'] = grid[1]
            self.xctls[name]['step']= grid[2]
        elif self.xctls[name]['xtype']=='MJOY':
            self.xctls[name]['min']= grid[0]
            self.xctls[name]['max'] = grid[1]
            self.xctls[name]['step']= grid[2]
            self.xctls[name]['min2']= grid[3]
            self.xctls[name]['max2'] = grid[4]
            self.xctls[name]['step2']= grid[5]
#-------------------------------------------------------------------------------
    def translate( self, name, p1,p2):
        self.xctls[name][ 'trans']=[p1,p2]
#-------------------------------------------------------------------------------
    def targets( self, name, targs):
        self.xctls[name][ 'targs']=targs
#-------------------------------------------------------------------------------
    def text_box( self, name, i, offset,vertical=False,label=True,nplace=6, integ=False):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )

        x += offset[0] # offset from x,y
        y += offset[1]
        valp5 = places(vals[i],nplace)
        if integ: # display integer only
            if valp5 < 0:
                valp5 = int(valp5-.5)
            else:
                valp5 = int(valp5+.5)
        numpix = self.txt.width * len( str(valp5)) +10
        if vertical:
            if label:
                self.txt.place(x, y-self.txt.height-5, nams[i], cols[i])
            arect=[ x, y-3, numpix, self.txt.height+6 ]
            pygame.draw.rect(self.screen, cols[i], arect, 2)
            self.txt.place( 5+x, y, str(str(valp5)) , cols[i])
        else: # place nams label to left
            if label:
                nampix = self.txt.width * len( nams[i] ) +8
                self.txt.place( x-nampix-2, y, nams[i], cols[i])
            arect=[ x, y-3, numpix, self.txt.height+6 ]
            pygame.draw.rect(self.screen, cols[i], arect, 2)
            self.txt.place(x+3, y, str(str(valp5)) , cols[i])
#-------------------------------------------------------------------------------
    def target_box( self, name, i, offset,vertical=False,label=True,nplace=6, integ=False):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        x += offset[0] # offset from x,y
        y += offset[1]
        valp5 = places( targs[i],nplace)
        if integ: # display integer only
            if valp5 < 0:
                valp5 = int(valp5-.5)
            else:
                valp5 = int(valp5+.5)
        numpix = self.txt.width * len( str(valp5)) +10
        if vertical:
            if label:
                self.txt.place(x, y-self.txt.height-5, nams[i], RED)
            arect=[ x, y-3, numpix, self.txt.height+6 ]
            pygame.draw.rect(self.screen, RED, arect, 2)
            self.txt.place( 5+x, y, str(str(valp5)) , RED)
        else: # place nams label to left
            if label:
                nampix = self.txt.width * len( nams[i] ) +8
                self.txt.place( x-nampix, y, nams[i], RED)
            arect=[ x, y-3, numpix, self.txt.height+6 ]
            pygame.draw.rect(self.screen, RED, arect, 2)
            self.txt.place(x+3, y, str(str(valp5)) , RED)
#-------------------------------------------------------------------------------
    def draw_gage_r1( self, name):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        wid = 120  # width of gage_r1
        tic = 25  # length of tics
        ysq = .4 # multiplyer for y dim squashing
        i=0
        for theta in drange( math.pi, math.pi*2, math.pi/36.):  #draw Gage R1
            if i%3 == 0:
                ttic=tic
                if i==18:
                    ttic = int(tic*1.5)
            else:
                ttic=tic/2
            i += 1
            xmp = 1 + abs(theta-math.pi*1.5)/2
            p1 = (math.cos(theta)*wid*xmp+x,math.sin(theta)*wid*ysq+y)
            p1t = (math.cos(theta)*wid*xmp+x,math.sin(theta)*wid*ysq+y+ttic)
            if theta > math.pi:
                pygame.draw.line(self.screen,WHITE,p1_last, p1,2 )
                pygame.draw.line(self.screen,WHITE,p1, p1t,2 )
            else:
                pygame.draw.line(self.screen,WHITE,p1, p1t,2 )
            p1_last = p1
        sz = len(vals)
        for i, vala in enumerate( vals ):
            v1ang = math.pi/360*vala + math.pi
            xmp = 1 + abs(v1ang-math.pi*1.5)/2
            p1va = ( math.cos(v1ang)*wid*xmp+x,math.sin(v1ang)*wid*ysq+y) #base
            p1vb = ( math.cos(v1ang+.02)*wid*xmp+x+6, math.sin(v1ang+.06)*(wid)*ysq+y-tic)
            p1vc = ( math.cos(v1ang-.02)*wid*xmp+x-6, math.sin(v1ang-.06)*(wid)*ysq+y-tic)
            poly = [ p1va, p1vb, p1vc ]
            pygame.draw.polygon( self.screen, cols[i], poly, 3)  # draw Arrow
            self.text_box( name, i, [124*i-(len(vals)-1)*50-15, 0] )
#-------------------------------------------------------------------------------
    def time_asc(self, name ):
        time_UTC = time.time()
        time_asc = time.ctime(int(time_UTC))
        [x,y] = self.xctls[name][ 'pos']
        self.txt.place( x, y, time_asc, BLUE)
#-------------------------------------------------------------------------------
    def value_rated( self, name, vala, i): # slow rate change for rated controls
        if self.xctls[name]['rate']<9999: # if rate is set for that control
            value = self.xctls[name]['value'][i]
            dif = (vala - value)
            newtime = time.time()
            self.xctls[name]['last_time'] = newtime
            interval = newtime - self.xctls[name]['last_time']
            if interval == 0:
                interval = .001
            drate = dif/interval
            if drate > self.xctls[name]['rate']:
                dif = self.xctls[name]['rate']*interval
                #print('vala, drate, dif, value=',vala,drate,dif, value+dif)
            elif drate < -self.xctls[name]['rate']:
                dif = -self.xctls[name]['rate']*interval
            value += dif
            self.xctls[name]['value'][i] = value
            return( value + dif)
        else:
            return( vala )
#-------------------------------------------------------------------------------
    def gage_parms( self, name ):
        pos = self.xctls[name][ 'pos']
        name1 = self.xctls[name]['lab_top']
        name2 = self.xctls[name]['lab_bot']
        nams = self.xctls[name][ 'src']
        vals=[]
        if self.xctls[name]['source']==True: # self is the source
            vals.append( self.value_rated( name, self.xctls[name][ 'value'][0],0))
            nams = [self.xctls[name]['lab_top']]
        else:
            for i, src in enumerate( nams ): # collect values from other sources
                vala = self.xctls[src]['value'][0]
                vals.append( self.value_rated( name, vala, i))
        cols = self.xctls[name][ 'color']
        grid = self.xctls[name][ 'grid']
        targs = self.xctls[name][ 'targs']
        return( pos, nams, vals, cols, grid, targs )
#------------------------------------------------------------------------------
    def draw_gage_r2(self, name ):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        rr = [160, 125]
        i=0
        for theta in drange( 0, math.pi*3, math.pi/18.):
            if i%3==0 :
                rt = [rr[0]-17,rr[1]-19]  # longer lines
            else:
                rt = [rr[0]-7,rr[1]-8]  # shorter lines
            i+=1
            p1 = (math.cos(theta)*rr[0]+x,math.sin(theta)*rr[0]+y)
            p1t = (math.cos(theta)*rt[0]+x,math.sin(theta)*rt[0]+y)
            p2 = (math.cos(theta)*rr[1]+x,math.sin(theta)*rr[1]+y)
            p2t = (math.cos(theta)*rt[1]+x,math.sin(theta)*rt[1]+y)
            if theta > math.pi/2:
                pygame.draw.line(self.screen,WHITE,p1_last, p1,2 )
                pygame.draw.line(self.screen,WHITE,p2_last, p2,2 )
                pygame.draw.line(self.screen,WHITE,p1, p1t,2 )
                pygame.draw.line(self.screen,WHITE,p2, p2t,2 )
            else:
                pygame.draw.line(self.screen,WHITE,p1, p1t,2 )
                pygame.draw.line(self.screen,WHITE,p2, p2t,2 )
            p1_last = p1
            p2_last = p2
        pygame.draw.line(self.screen,WHITE,(x-rr[0],y), (x-rr[1]+25,y),2 )
        self.txt.place( x-15, y-143, '180', WHITE)
        self.txt.place( x-5, y+128, '0', WHITE)
        for i, vala in enumerate( vals ):   # draw the arrows
            v1ang = math.pi/180*vals[i] + math.pi/2
            p1va = (math.cos(v1ang)*rr[i]+x,math.sin(v1ang)*rr[i]+y)
            p1vb = (math.cos(v1ang+.05)*(rr[i]+20)+x,math.sin(v1ang+.05)*(rr[i]+20)+y)
            p1vc = (math.cos(v1ang-.05)*(rr[i]+20)+x,math.sin(v1ang-.05)*(rr[i]+20)+y)
            poly = [p1va,p1vb,p1vc]
            pygame.draw.polygon(self.screen,cols[i],poly,0 )

        offs=[[-200,-135],[-200,130]]
        for i in range(0,2):
            self.text_box( name, i, offs[i], vertical=True )
#------------------------------------------------------------------------------
    def draw_maxis( self, name):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        rr = 70
        i=0
        nvals = (grid[1]-grid[0])
        divisions = nvals/grid[2]
        needle_theta = vals[0] /nvals * math.pi*2
        p1 = (math.cos(needle_theta)*(rr+10)+x,math.sin(needle_theta)*(rr+10)+y)
        p1t = (math.cos(needle_theta)*(rr-30)+x,math.sin(needle_theta)*(rr-30)+y)
        pygame.draw.line(self.screen,GREEN,p1, p1t,4 )
        for theta in drange( 0, math.pi*2, math.pi/(divisions/2)):
            if theta==0:
                p1_last = (math.cos(theta)*rr+x,math.sin(theta)*rr+y)
            if i%grid[3]==0 :
                rt =rr-15  # longer lines
            else:
                rt =rr-7
            i+=1
            p1 = (math.cos(theta)*rr+x,math.sin(theta)*rr+y)
            p1t = (math.cos(theta)*rt+x,math.sin(theta)*rt+y)
            pygame.draw.line(self.screen,WHITE,p1_last, p1,2 )
            pygame.draw.line(self.screen,WHITE,p1, p1t,2 )
            p1_last = p1
        self.text_box( name, 0, [-28,0] ,vertical=True, label=True )

#------------------------------------------------------------------------------
    def draw_hdot( self, name):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        rr=70
        pi2=math.pi*2
        pi1=math.pi
        tw = .20944
        a=[-500, -100, -50, -30, -10, 0, 10, 30, 50, 100, 500]
        b=[ 2.667*pi1, pi2+tw*4, pi2+tw*3, pi2+tw*2, pi2+tw, pi2,
                    pi2-tw, pi2-tw*2, pi2-tw*3, pi2-tw*4, 1.333*math.pi]
        offs = [[-90,13],[0,13],[145,13]]
        toffs = [[-90,43],[0,43],[145,43]]
        for i in range(0, 3):
            self.text_box( name, i, offs[i], label=False, integ=True )
            if targs[i] != None:
                self.target_box( name, i, toffs[i], label=False, integ=True )
            self.txt.place(  x+offs[i][0]+17,y-9,'H', WHITE)
            for j in range(0,i):
                pygame.draw.circle( self.screen, WHITE,[x+offs[i][0]+j*10+28-i*4, y-13], 3, 3 )
        i=0
        strt = math.pi*1.333
        endd = math.pi*2.667
        p1_last = (math.cos(strt)*rr+x+30,math.sin(strt)*rr+y+37)
        rg = 75
        rg2 = 78
        tg = 65
        g_last = (math.cos(strt)*rg+x+30,math.sin(strt)*rg+y+37)
        g2_last = g_last
        tg_last = [math.cos(strt)*tg+x+27,math.sin(strt)*tg+y+37]
        vr1 = jlookup(a,b,vals[1])
        tg1 = jlookup(a,b,targs[1])
        for theta in drange( strt, endd, math.pi/15.):
            i+=1
            rt = 55
            if theta > pi2-.1 and theta < pi2+.1:
                rt = 40
            p1 = (math.cos(theta)*rr+x+30,math.sin(theta)*rr+y+37)  # curve point
            p1t = (math.cos(theta)*rt+x+30,math.sin(theta)*rt+y+37) # tic point
            p1g = [math.cos(theta)*rg+x+32,math.sin(theta)*rg+y+37] # gage point
            p2g = [math.cos(theta)*rg2+x+27,math.sin(theta)*rg2+y+37] # gage point
            tgg = [math.cos(theta)*tg+x+27,math.sin(theta)*tg+y+37] # target point
            if targs[1]<=0 and theta < tg1 and theta>=2*math.pi or   \
               targs[1]>=0 and theta > tg1 and theta<=2*math.pi and targs[1] != None:
                pygame.draw.line(self.screen, RED, tgg_last, tgg, 8 )
            if vals[1]<=0 and theta < vr1 and theta>=2*math.pi or   \
               vals[1]>=0 and theta > vr1 and theta<=2*math.pi:
                pygame.draw.line(self.screen,cols[1],g_last, p1g,8 )
                pygame.draw.line(self.screen,cols[1],g2_last, p2g,8 )
                if vals[1]<15 and vals[1]>-15:
                    p1g[0] -= 6
                    p2g[0] += 6
                    pygame.draw.line(self.screen,cols[1], p1g, p2g,10 )
            pygame.draw.line(self.screen,WHITE,p1_last, p1,2 )
            pygame.draw.line(self.screen,WHITE,p1, p1t,2 )
            p1_last = p1
            g_last = p1g
            g2_last = p2g
            tgg_last = tgg
#------------------------------------------------------------------------------
    def draw_gage_x(self, name):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        ntics = 11  # always 11 tics per scale
        if len(vals)>1: #change grid if both do not fit
            gwidth = (ntics-1)*grid
            vrange = abs(vals[0] - vals[1])*2
            for i in range(1,len(vals)):
                rangi = abs(vals[0]-vals[i])
                if rangi > vrange:
                    vrange=rangi
            while gwidth < vrange:
                grid *=2
                gwidth =(ntics-1)*grid
        pptic = 2 * self.txt.width +4       # pixels per tic
        chptic = int( pptic/self.txt.width)  # characters possible per tic
        max_val = vals[0] + grid*5  # end value
        idx=0
        max_sz = len(str(max_val))      # size of max value
        tics_per_val = int(max_sz/chptic+.5)
        half_scale = 7*pptic            # pixels to half_scale
        midval = int((vals[idx]/grid+.5))*grid  # mid scale val
        first = midval - grid*5
        pos1=int(x-half_scale)          # x pos of 1st value
        pygame.draw.line( self.screen,WHITE, [pos1,y], [int(pos1+(ntics-1)*pptic),y],2 )
        v1st = str(int(first))
        cenlen = (len(v1st)+2)*self.txt.width  # space for center gage value
        gglen = ntics* pptic + self.txt.width*len(v1st) # gage space
        nscales = int((gglen-cenlen)/cenlen+.5) # number posible scales
        for i in range(0,ntics):
            scal=i*grid+first
            xcen = x - half_scale + i*pptic
            xx = xcen - int(len(str(scal))/2*self.txt.width) + self.txt.width/2
            pygame.draw.line( self.screen,WHITE, [xcen,y], [xcen,y+10],2 )
            if i==0 or i==5 or i==10:   #if scale drawn tics
                self.txt.place( xx, y+12, str(scal), WHITE)
        if len(vals)==2:  #kz must make it any size
            vstr = str(places(vals[1],5))
            ax = pos1 + pptic*(vals[1]-first)/grid
            arrow1 = [(ax,y), (ax-5, y-23), (ax+5, y-23), (ax,y)]
            pygame.draw.polygon( self.screen, cols[1], arrow1,0 )
        if len(vals)==1:
            offs = [[-30,35]]
        elif len(vals)==2:
            offs = [[-100,35],[40,35]]
        else: #assume 3
            offs = [[-130,35],[-30,35],[70,35]]
        for i in range(0, len(vals)):
            offset = [ 70*(1-i-(len(vals)-1))+35, 35]
            self.text_box( name, i, offs[i] )
        val1s = places(vals[0],5)
        ax = pos1 + pptic*(val1s-first)/grid
        arrow2 = [(ax,y), (ax-5, y-23), (ax+5, y-23), (ax,y)]
        pygame.draw.polygon( self.screen,cols[0], arrow2, 2 )
#------------------------------------------------------------------------------
    def mouseb_caption( self, name, num,  value):
        touches = self.xctls[name]['touches']
        rect,pressed,color,colorh,cap = touches[num]
        cap = value
        touches[num]=[rect,pressed,color,colorh,cap]
#------------------------------------------------------------------------------
    def mouseb_pressed( self, name, num,  value):
        touches = self.xctls[name]['touches']
        rect,pressed,color,colorh,cap = touches[num]
        pressed = value
        touches[num]=[rect,pressed,color,colorh,cap]
#------------------------------------------------------------------------------
    def draw_gage_y(self, name ): # big gage_y
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        ntics = 10  # always 10 tics per scale
        pptic = self.txt.height +4
        tics_per_val = 1
        midticval =  float(int( vals[0] / grid)) * grid
        p_to_mid = (midticval- vals[0])/ grid * pptic
        first =  midticval + 5*grid
        pos1 = y - p_to_mid - pptic*5
        pygame.draw.line( self.screen,WHITE, [x,pos1], [x,int(pos1+ntics*pptic)],2 )
        v1st = str(int(first))
        cenlen = (len(v1st)+2)*self.txt.width  # space for center gage value
        gglen = ntics* pptic + self.txt.width*len(v1st) # gage space
        nscales = int((gglen-cenlen)/cenlen+.5) # number posible scales
        self.txt.place( x+7, y-pptic*5-25, nams[0], cols[0])
        for i in range(0,ntics+1):
            scal = int( first - i*grid)
            ypos = pos1 + i*pptic
            pygame.draw.line( self.screen,WHITE, [x,ypos], [x+14,ypos],2 )
            if (i%tics_per_val)==0:  #if scale drawn tic
                self.txt.place( x+22, ypos-pptic/2+4, str(scal), WHITE)
        vstr = places(vals[0],5)
        pygame.draw.line( self.screen,WHITE, [x,y], [x+75,y],2 )
        self.text_box( name, 0, [74,-10], label=False )
#------------------------------------------------------------------------------
    def draw_gage_ys(self, name ):  # small Y gage
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
        ntics = 8  # always 8 tics per scale
        pptic = self.txt.height
        tics_per_val = 1
        midticval =  float(int( vals[0] / grid)) * grid
        p_to_mid = (midticval- vals[0])/ grid * pptic
        first =  midticval + 4*grid
        pos1 = y - p_to_mid - pptic*(ntics//2)
        # draw verticle line
        pygame.draw.line( self.screen,WHITE, [x,pos1], [x,int(pos1+ntics*pptic)],2 )
        v1st = str(int(first))
        cenlen = (len(v1st)+2)*self.txt.width  # space for center gage value
        gglen = ntics* pptic + self.txt.width*len(v1st) # gage space
        nscales = int((gglen-cenlen)/cenlen+.5) # number posible scales
        self.txt.place( x+7, y-pptic*3-40, nams[0], cols[0])
        for i in range(0,ntics+1):
            scal = int( first - i*grid)
            ypos = pos1 + i*pptic
            pygame.draw.line( self.screen,WHITE, [x,ypos], [x+14,ypos],2 )
            if (i%tics_per_val)==0:  #if scale drawn tic
                self.txt.place( x+22, ypos-pptic/2+4, str(scal), WHITE)
        vstr = places(vals[0],5)
        pygame.draw.line( self.screen,WHITE, [x,y], [x+65,y],2 )
        self.text_box( name, 0, [65,-10], label=False )
#------------------------------------------------------------------------------
    def draw_mjoy( self, name):
        [x,y], nams, vals, cols, grid, targs = self.gage_parms( name )
#------------------------------------------------------------------------------
    def make( self, name, xtype, src, pos):  # make a control
        if name not in self.xctls: #if not already defined stuff these into it
            xobj=xobj_args( name, xtype, src, pos)
            self.xctls[name]= xobj  # arg dictonarys are indexed as dictionary
            self.xctls[name]['display']=False # default to no display
            self.xctls[name]['first_time']=time.time() #when did we start control?
            self.xctls[name]['targs'] = [None]*len(src) # make targs null for sources
        elif xtype != 'SET_DATA' and xtype != 'SET_ACTION':
            print('Warning: making second instance of ',name)
        if xtype=='SW2' or xtype=='BSW':
            self.xctls[name][ 'value']=[False]
            touches = self.build_mouseBSW(  pos )
            self.xctls[name]['touches']=touches
            return(True)
        elif xtype=='SET_DATA':
            self.xctls[name]['data'][src]=pos
        elif xtype=='SET_ACTION':
            self.xctls[name]['action'][src]=pos
        elif xtype=='HAT':
            return(0)
        elif xtype=='GAGE_Y':
            self.xctls[name]['grid']=10 # default grid width
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            return(0)
        elif xtype=='GAGE_YS':
            self.xctls[name]['grid']=15 # default grid width
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            return(0)
        elif xtype=='PARAM':
            self.xctls[name]['value'][0]=src[0] #initial value in PARAM case
            return(0)
        elif xtype=='GAGE_X':
            self.xctls[name]['grid']=10 # default grid width
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            return(0)
        elif xtype=='GAGE_R1':
            self.xctls[name]['grid']=10 # default grid width
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            return(0)
        elif xtype=='GAGE_R2':
            self.xctls[name]['grid']=10 # default grid width
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            return(0)
        elif xtype=='MAP':
            return(0)
        elif xtype=='HDOT':
            self.xctls[name]['grid']=10 # default grid width
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            return(0)
        elif xtype=='MAXIS': # Mousewheel Axis type
            self.xctls[name]['grid']=[0,360,10,3] # default grid width
            self.xctls[name]['rate']=1 # default mousewheel change rate
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            self.xctls[name]['value'][0]=src[0] #initial value
            self.xctls[name]['source']=True # MAXIS is a source of data
            self.xctls[name]['lab_top']= name  #default label is maxis name
            return(0)
        elif xtype=='AXIS':
            return(0)
        elif xtype=='AXIS2':
            return(0)
        elif xtype=='MULTI':  # make a multi switch
            return(0)
        elif xtype=='MOUSEB': # mouse button 1 and touch switch button
             do_radio=True
             touches,args=self.build_mouseButns( src[0], GREY_B, GREEN_HI, \
                                        do_radio, pos)
             self.xctls[name]['touches']=touches
             self.xctls[name]['args']=args
             return(0)
        elif xtype=='Screen':  # screen switch
             return(0)
        elif xtype=='SLIDER_Y':  # vertical slider
             x,y = pos
             xobj['slidPos'] = 0
             xobj['shape'] = (35, 520 )
             xobj['rect'] = pygame.Rect(x-10, y-10, 35+20, 520+20)
             xobj['min']=0
             xobj['max']=100
             return(0)
        elif xtype=='SLIDER_X':  # horizontal slider
             x,y = pos
             xobj['slidPos'] = 0
             xobj['shape'] = (360, 35 )
             xobj['rect'] = pygame.Rect(x, y, 360, 35)
             xobj['min']=0
             xobj['max']=100
             return(0)
        elif xtype=='TIME':  # display of time
            return(0)
        elif xtype=='TIMER':  # Timer
            return(0)
        elif xtype == 'TXIN':  # text input box
            self.xctls[name]['active'] = False
            self.xctls[name]['value'][0] =''
            x,y = pos
            self.xctls[name]['rect'] = pygame.Rect(x, y-16, src[0], 32)
        elif xtype == 'TXOUT': # text output
            self.xctls[name]['color']=COLS_DEF #deflt colrs
            self_sourced = not src[0] in self.xctls.keys()
            self.xctls[name]['source'] = self_sourced
            if self_sourced:
                self.xctls[name]['value'][0] = src[0]
            else:
                self.xctls[name]['value'][0] =''
        elif xtype=='MJOY':
            x,y = pos
            xobj['value'] = [0,0]
            xobj['shape'] = (200, 200, 20)
            xobj['rect'] = pygame.Rect(x-1, y-1, 202, 202)
            xobj['min']=-49.5
            xobj['max']=49.5
            xobj['step']=1
            xobj['min2']=-49.5
            xobj['max2']=49.5
            xobj['step2']=1
            return(0)
        elif xtype=='NONE':
            return(0)
        return ( True)
#-------------------------------------------------------------------------------
    def draw_all(self ):
        keys = self.xctls.keys()
        for name in keys:
            xarg = self.xctls[name]
            if xarg['xtype']=='AXIS':
                if xarg['display']:
                    textString = xarg['lab_top'] + ":  \
                         {:>6.2f}".format(xarg['value'][0])
                    textBitmap = self.font.render(textString, True, WHITE)
                    self.screen.blit(textBitmap, (xarg['pos'][XX], xarg['pos'][YY]))
            elif xarg['xtype']=='SW2' or xarg['xtype']=='BSW':
                wide=3
                half1= len(xarg['lab_top'])*4
                textBitmap = self.font.render(xarg['lab_top'], True, WHITE)
                self.screen.blit(textBitmap, (xarg['pos'][XX]-half1, xarg['pos'][YY]-40)) #above
                half2= len(xarg['lab_bot'])*4
                textBitmap2 = self.font.render(xarg['lab_bot'], True, WHITE)
                self.screen.blit(textBitmap2, (xarg['pos'][XX]-half2, xarg['pos'][YY]+25)) #below
                pygame.draw.circle(self.screen,WHITE, (xarg['pos'][XX],xarg['pos'][YY]),15,wide)
                if xarg['value'][0]: #switch is ON
                    rect=pygame.Rect(xarg['pos'][XX]-5, xarg['pos'][YY]-24, 10, 24)
                else: #switch is OFF
                    rect=pygame.Rect(xarg['pos'][XX]-5, xarg['pos'][YY], 10, 24)
                pygame.draw.rect(self.screen,WHITE,rect)
            elif xarg['xtype'] == 'GAGE_X':
                self.draw_gage_x( name )
            elif xarg['xtype'] == 'GAGE_Y':
                self.draw_gage_y( name )
            elif xarg['xtype'] == 'GAGE_YS':
                self.draw_gage_ys( name )
            elif xarg['xtype'] == 'GAGE_R1':
                self.draw_gage_r1( name )
            elif xarg['xtype'] == 'HDOT':
                self.draw_hdot( name )
            elif xarg['xtype'] == 'MAXIS':
                self.draw_maxis( name )
            elif xarg['xtype'] == 'GAGE_R2':
                self.draw_gage_r2( name )
            elif xarg['xtype'] == 'MOUSEB':
                touches = xarg['touches']
                bargs = xarg['args']
                for i, item in enumerate( touches ):
                    rect,pressed,color,colorh,cap = item
                    x,y,wd,ht=rect
                    xplus = (wd - self.txt.width *len( cap ))/2-7  #zz
                    if pressed:
                        pygame.draw.rect( self.screen, colorh, rect)
                        self.txt.place( x+xplus,y+10, cap, XBLACK)
                    else:
                        pygame.draw.rect( self.screen, color, rect)
                        self.txt.place( x+xplus,y+10, cap, WHITE)
            elif xarg['xtype'] == 'SLIDER_Y':
                x,y=xarg['pos']
                pygame.draw.rect(self.screen, GREY_B, (x, y, xarg['shape'][0], xarg['shape'][1]), 0)
                bpos =  y + xarg['shape'][1]-xarg['slidPos']
                pygame.draw.rect(self.screen,GREEN_HI,(x, bpos,xarg['shape'][0], xarg['slidPos']))
                ystr = self.txt.width*len(name)//2
                self.txt.place( x-ystr+20, y-35, name, GREEN)
                ybot = y+xarg['shape'][1]+7
                value = str(xarg['value'][0])
                numpix = self.txt.width * len(value ) +10
                arect=[ x, ybot, numpix, self.txt.height+6 ]
                pygame.draw.rect(self.screen, WHITE, arect, 0)
                self.txt.place(x+3, ybot , value , XBLACK)
            elif xarg['xtype'] == 'MJOY':  # mouse based joystick
                x,y=xarg['pos']
                _width,_height,handle_rad = xarg['shape']
                pygame.draw.rect( self.screen, GREY_B, (x, y, _width, _height))
                circle = (int(x + (xarg['value'][0] - xarg['min']) /                   \
                                            (xarg['max'] -  xarg['min']) * _width),
                                 int(y + (xarg['max'] - xarg['value'][1]) /            \
                                            (xarg['max'] - xarg['min2']) *_height))
                gfxdraw.filled_circle( self.screen, circle[0], circle[1], handle_rad, GREEN_HI)
                gfxdraw.aacircle( self.screen, circle[0], circle[1], handle_rad, XBLACK)
                ybot = y+xarg['shape'][1]+7
                xvalue = str(xarg['value'][0])
                numpix = self.txt.width * len(xvalue ) +10
                arect=[ x, ybot, numpix, self.txt.height+6 ]
                pygame.draw.rect(self.screen, WHITE, arect, 0)
                self.txt.place(x+3, ybot , xvalue , XBLACK)
                yvalue=str(xarg['value'][1])
                numpix = self.txt.width * len( yvalue ) +10
                xbot = x+xarg['shape'][1]-numpix
                arect=[ xbot , ybot, numpix, self.txt.height+6 ]
                pygame.draw.rect(self.screen, WHITE, arect, 0)
                self.txt.place(xbot, ybot , yvalue , XBLACK)
            elif xarg['xtype'] == 'SLIDER_X':
                x,y=xarg['pos']
                pygame.draw.rect(self.screen, GREY_B, (x, y, xarg['shape'][0], xarg['shape'][1]), 0)
                bpos =  y + xarg['shape'][1]-xarg['slidPos']
                pygame.draw.rect(self.screen,GREEN_HI,(x,y, xarg['slidPos'], xarg['shape'][1] ))
                ystr = self.txt.width*len(name)//2
                self.txt.place( x-ystr+xarg['shape'][0]//2, y-35, name, GREEN)
                ybot = y+xarg['shape'][1]+7
                value = str(xarg['value'][0])
                numpix = self.txt.width * len(value ) +10
                arect=[ x, ybot, numpix, self.txt.height+6 ]
                pygame.draw.rect(self.screen, WHITE, arect, 0)
                self.txt.place(x+3, ybot , value , XBLACK)
            elif xarg['xtype'] == 'TIME':
                self.time_asc(name)
            elif xarg['xtype'] =='SET_ACTION':
                for item in xarg['action']:
                    if button_flag[item]:
                        xarg['action'][item]()
            elif xarg['xtype'] == 'TXIN':  # text input box
                if xarg['active']:
                    pygame.draw.rect(self.screen, LTBLUE, xarg['rect'] )
                    pygame.draw.rect(self.screen, PURPLE, xarg['rect'], width=3)
                else:
                    pygame.draw.rect(self.screen, GREY_B, xarg['rect'] )
                    pygame.draw.rect(self.screen, WHITE, xarg['rect'], width=3)
                x= xarg['pos'][XX]
                y= xarg['pos'][YY]
                self.txt.place(x+5, y-self.txt.height+10, xarg['value'][0], XBLACK)
            elif xarg['xtype'] == 'TXOUT':  # text output
                x,y= xarg['pos']
                if self.xctls[name]['source']==True: # self is the source
                    vala = self.xctls[name]['value'][0]
                else: # then get the reference source value
                    src = self.xctls[name][ 'src']
                    vala = self.xctls[src[0]][ 'value'][0]
                self.txt.place(x+5, y-self.txt.height+10, vala, GREEN)
#------------------------------------------------------------------------------
    def round(self, value, step):
        return( step * round(value / step))
#--------------------------- end of draw_all -----------------------------------
    def update_all(self ):
        global last_mouse, mevent

        keys = self.xctls.keys() # go through all named xctl's dictionary
        for name in keys:    # names of each conrol
            xarg = self.xctls[name] # each control is a dictionary
            if self.JOY:
                joystick = pygame.joystick.Joystick(0)
            if xarg['xtype'] == 'BUTTON':
                if self.JOY:
                    xarg['value'][0] = joystick.get_button( xarg['src'][0])
            elif xarg['xtype'] =='SET_DATA':
                for item in xarg['data']:
                    if button_flag[item]:
                        parameter[name]=xarg['data'][item]

            elif xarg['xtype'] == 'BSW': # button switch
                if self.JOY:
                    this_value = joystick.get_button( xarg['src'][0])
                else:
                    this_value=0
                switched = this_value > xarg['lastval'] #rising edge
                xarg['lastval'] = this_value
                if switched:
                    if xarg['value'][0]:
                        xarg['value'][0]=False # switching off
                    else:
                        xarg['value'][0] = True # switching on
            elif xarg['xtype'] == 'SW2': # two button solenoid switch
                this_value=0
                if self.JOY:
                    B_ON = joystick.get_button( xarg['src'][0])
                    B_OFF = joystick.get_button( xarg['src'][1])
                    if B_OFF==1:
                            xarg['value'][0]=False
                    if B_ON==1:
                            xarg['value'][0] = True
                else: # no joystick so do same as BSW
                    switched = this_value > xarg['lastval'] #rising edge
                    xarg['lastval'] = this_value
                    if switched:
                        if xarg['value'][0]:
                            xarg['value'][0]=False # switching off
                        else:
                            xarg['value'][0] = True # switching on
            elif xarg['xtype'] == 'AXIS':
                if self.JOY:
                    jval = joystick.get_axis( xarg['src'][0])
                    [a,b] = xarg['trans']
                    val = jlookup( a, b , jval )
                    dif = (val - xarg['value'][0])
                    newtime = time.time()
                    interval = newtime - xarg['last_time']
                    if interval == 0:
                        interval = .001
                    xarg['last_time'] = newtime
                    drate = dif/interval
                    if drate > xarg['rate']:
                        dif = xarg['rate']*interval
                    if drate < -xarg['rate']:
                        dif = -xarg['rate']*interval
                    xarg['value'][0] = xarg['value'][0] + dif
                else:  # no joystick
                    jval = 0
                    xarg['value'][0] = 0
            elif xarg['xtype'] == 'GAGE_Y':
                pass
            elif xarg['xtype'] == 'SLIDER_Y':
                mousePos = pygame.mouse.get_pos()
                x,y = xarg['pos']
                if xarg['rect'].collidepoint( mousePos):
                    if pygame.mouse.get_pressed()[0]:
                        epos = y + xarg['shape'][1]
                        xarg['slidPos'] =  epos - mousePos[1]
                        if xarg['slidPos'] < 1:
                            xarg['slidPos'] = 0
                        if xarg['slidPos'] > xarg['shape'][1]:
                            xarg['slidPos'] = xarg['shape'][1]
                        # now determine the value at slidpos
                        dim = xarg['shape'][1]-6
                        mpos = float(xarg['slidPos']) -4
                        perc = places( mpos/float(dim),3)
                        value = places( perc*float(xarg['max']-xarg['min'])+xarg['min'],3)
                        if value<xarg['min']:
                            value = xarg['min']
                        elif value >xarg['max']:
                            value = xarg['max']
                        xarg['value'][0]=value
            elif xarg['xtype'] == 'SLIDER_X':
                mousePos = pygame.mouse.get_pos()
                x,y = xarg['pos']
                if xarg['rect'].collidepoint( mousePos):
                    if pygame.mouse.get_pressed()[0]:
                        xarg['slidPos'] =  mousePos[0] - x
                        if xarg['slidPos'] < 1:
                            xarg['slidPos'] = 0
                        if xarg['slidPos'] > xarg['shape'][0]:
                            xarg['slidPos'] = xarg['shape'][0]
                        # now determine the value at slidpos
                        dim = xarg['shape'][0]-6
                        mpos = float(xarg['slidPos']) -4
                        perc = places( mpos/float(dim),3)
                        value = places( perc*float(xarg['max']-xarg['min'])+xarg['min'],3)
                        if value<xarg['min']:
                            value = xarg['min']
                        elif value >xarg['max']:
                            value = xarg['max']
                        xarg['value'][0]=value
            elif xarg['xtype'] == 'MOUSEB': # mouse touch buttons
                touches=xarg['touches']
                for i, item in enumerate(touches):
                    rect,pressed,color,colorh,cap = item
                    button_flag[cap]=pressed  # update button pressed states
            elif xarg['xtype'] == 'TXIN':  # text input box
                pass
            elif xarg['xtype'] == 'TXOUT':  # text output
                pass
            elif xarg['xtype'] == 'MJOY':  # mouse based joystick
                mousePos = pygame.mouse.get_pos()
                x,y = xarg['pos']
                if xarg['rect'].collidepoint( mousePos):
                    if pygame.mouse.get_pressed()[0]:
                        mousex,mousey = mousePos
                        shapex,shapey,rads = xarg['shape']
                        rng = xarg['max'] - xarg['min']
                        xpos = mousex - x
                        ypos = mousey - y
                        valx = xpos / shapex * rng + xarg['min']
                        valx = self.round( valx, xarg['step'] )
                        valx = max(min(valx, xarg['max']), xarg['min'])
                        rng2 = xarg['max2'] - xarg['min2']
                        valy = xarg['max2'] - ypos / shapey * rng2
                        valy = self.round( valy, xarg['step2'] )
                        valy = max(min(valy, xarg['max']), xarg['min2'])
                        xarg['value'][0]= valx
                        xarg['value'][1]= valy
                    else: # release joystick to center position
                        xarg['value'][0]=  xarg['min'] +  xarg['max']
                        xarg['value'][1]=  xarg['max2'] +  xarg['min2']
                elif not pygame.mouse.get_pressed()[0]:
                    xarg['value'][0]=  xarg['min'] +  xarg['max']
                    xarg['value'][1]=  xarg['max2'] +  xarg['min2']
#------------------------------------------------------------------------------
xreg=[]  # list of registered xcons for update_all & draw_all processing
def Xregister( Xcontrol, mbutdef, **kwargs):
    always = kwargs.get('always', False)
    if len(mbutdef) != 2:  # if main xcon?
        bgroup=''
        bnum=''
    else:
        bgroup,bnum=mbutdef
    xreg.append([Xcontrol, always, bgroup, bnum])
#---------------------------------------------------------------------------
def jlookup( a, b, val):  # translate val to lookup table  a -translate-> b
    if val <= a[0]:
        return( float(b[0]) )
    size=len(a)
    if val >= a[size-1]:
        return( float(b[size-1]) )
    idx=0
    while idx<size and val > a[idx] :
        idx += 1
    return(float((b[idx]-b[idx-1])*(val-a[idx-1])/(a[idx]-a[idx-1])+b[idx-1]))
#------------------------------------------------------------------------------
def process_xcons():  # process xcontrol class update_all & draw_all
    done = process_events( )
    xcon = xreg[0][0]  # Kludge to get main xcon (find a better way))
    for xlist in xreg:
        Xcontrol, always, bgroup, bnum = xlist
        if always:
            Xcontrol.update_all()
            Xcontrol.draw_all()
        else: # check that the registered button is on before processing
            xarg = xcon.xctls[bgroup]
            touches = xarg['touches']
            rect,pressed,color,colorh,cap = touches[ bnum]
            if pressed:
                Xcontrol.update_all()
                Xcontrol.draw_all()
    return( done)
#------------------------------------------------------------------------------
def process_events(  ):
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    xcon = xreg[0][0]  # Kludge to get main xcon (find a better way))
    events = pygame.event.get()
    for event in events: # User did something.
        if event.type == MOUSEBUTTONDOWN :
            pos=pygame.mouse.get_pos()
            btn=pygame.mouse
            for xlist in xreg: #check registered xcons
                Xcontrol, always, bgroup, bnum = xlist
                if always: # is it always active ?
                    Xcontrol.mouse_event( event, pos) # always process
                else: # check that xcontrol is available to process
                    xarg = xcon.xctls[bgroup]
                    touches = xarg['touches']
                    rect,pressed,color,colorh,cap = touches[ bnum]
                    if pressed:
                        Xcontrol.mouse_event( event, pos) # always process
        elif event.type == MOUSEWHEEL:
            for xlist in xreg: #check registered xcons
                Xcontrol, always, bgroup, bnum = xlist
                if always: # is it always active ?
                    Xcontrol.mouse_event_wh( event, pos) # always process
                else: # check that xcontrol is available to process
                    xarg = xcon.xctls[bgroup]
                    touches = xarg['touches']
                    rect,pressed,color,colorh,cap = touches[ bnum]
                    if pressed:
                        Xcontrol.mouse_event_wh( event, pos) # always process
        elif event.type == pygame.JOYBUTTONUP:
            pass
            #print('joy_button_up', event)
        elif event.type == pygame.JOYHATMOTION:
            pass
            #print('joy_hat_motion')
        elif event.type == pygame.JOYHATMOTION:
            pass
            #print('joy_hat_motion')
        elif event.type == pygame.JOYAXISMOTION:
            pass
            #print('joy_axis_motion')
        elif event.type == pygame.JOYBALLMOTION:
            print('pygame.JOYBALLMOTION')
        elif event.type == pygame.MOUSEMOTION:
            for xlist in xreg: #check registered xcons
                Xcontrol, always, bgroup, bnum = xlist
                Xcontrol.mouse_event_txin( event, event.pos) # check TXIN's'
        elif event.type==pygame.KEYDOWN:
            procd = False
            for xlist in xreg: #check registered xcons
                Xcontrol, always, bgroup, bnum = xlist
                res = Xcontrol.mouse_event_txkey( event)
                if res: # if anything stole the event
                    procd = True
            if not procd:
                key_event( event) # OK to do if not processed already
        elif event.type == pygame.QUIT: # If user clicked close.
            return( True) # done = True

    return( False)

