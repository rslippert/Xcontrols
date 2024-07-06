import sys
import pygame
from pygame.locals import *
import time
from math import *
from screeninfo import get_monitors
from functools import *
from sys import path
path.append( './src' )
from xcontrols import *

screen_size=(1600, 900) # application screen size
S1SZ = (700,700)        # standard size of mission pictures
sub_screen = (945,50)   # position of sub screen pictures
#BCenter =[4150,3000]    # center position of moon map
moon_radius = 1737400 # meters
site1=( 89.498 , 222.000 )

#-----------------Load Images ----------------------------
pygame_icon = pygame.image.load(r'Missions\Artemis.png')
m_asc=pygame.image.load(r'Missions\Ascent.png')
Batts = pygame.image.load(r'Missions\Batterys.png')
m_dsc=pygame.image.load(r'Missions\Descent.png')
Doc = pygame.image.load(r'Missions\Docking.png')
Engs = pygame.image.load(r'Missions\Engine.png')
m_gway=pygame.image.load(r'Missions\Gateway_Orbit.png')
#moonB=pygame.image.load(r'Missions\grey_strip_10mpp_B.png')
moon=pygame.image.load(r'Missions\grey_site1&4.png')
m_target=pygame.image.load(r'Missions\Targets.png')
m_hls=pygame.image.load(r'Missions\HLS.png')
m_land=pygame.image.load(r'Missions\Lunar_Landing.png')
m_track=pygame.image.load(r'Missions\mission_track2.png')
m_nri=pygame.image.load(r'Missions\OCP_to_NRI.png')
m_out=pygame.image.load(r'Missions\Outbound.png')
m_ret=pygame.image.load(r'Missions\Return.png')
m_ice=pygame.image.load(r'Missions\Shackleton_Ice_5b.png')
m_site_1a=pygame.image.load(r'Missions\Shackleton_Sites.png')
m_site1=pygame.image.load(r'Missions\site1.png')
m_xcontrols=pygame.image.load(r'Missions\xcontrols.png')
nrho=pygame.image.load(r'Missions\nrho.png')

#moon_B = {'file':moonB, 'mpp':10, 'spole': [6100, 2500]}
moon_14 ={'file':moon,  'mpp': 5, 'spole': [6200, 744]}
moon = moon_14

#-------------- return x and y components of a vector ----------------
def vect_to_xy (t_deg, d ):
  rads = radians(t_deg)
  x = cos(rads)*d
  y = sin(rads)*d
  return x,y
#-------------------------------------------------------------------------------
def pol_to_pixel( polar, S_pole, mpp ): # return a pixel position
    moon_radius = 1737400.0 # meters radius of moon average at pole
    mpdeg = pi * moon_radius/180.0
    pixels_per_deg = mpdeg/mpp
    r = (90-polar[0])*pixels_per_deg
    ang = polar[1]*pi/180.
    return( [ int(S_pole[0]+sin(ang)*r+.5), int(S_pole[1]-cos(ang)*r+.5)] )
#-------------------------------------------------------------------------------
def set_map_center( msrc, polar ): # set target center on B strip
    global BCenter
    BCenter = pol_to_pixel( polar, msrc['spole'], msrc['mpp'] )
#-------------------------------------------------------------------------------
def get_map_center( msrc, deg_S, deg_E ): # set target center on B strip
    polar = [ deg_S, deg_E ]
    return( pol_to_pixel( polar, msrc['spole'], msrc['mpp'] ))
#-------------------------------------------------------------------------------
last_finger = False #turned on by mouse events, off by update
fevent=[]
def finger_event( button, pos):
    last_finger = True
    fevent=[ pos[0], pos[1]]  # to process later with update
#-------------------------------------------------------------------------------
def do_blit( flag, pos): # plot sub_screen defined by a parameter
    screen.blit( parameter[flag], pos)
#-------------------------------------------------------------------------------
def blit_with_rect( src, dst, deg_S, deg_E, xsize,ysize ):
    screen.blit( src, dst, ( xaxis['value'][0], yaxis['value'][0], xsize, ysize))
#-------------------------------------------------------------------------------
def blit_moon_map( msrc, dst, deg_S, deg_E, xsize,ysize ):
    xy = get_map_center( msrc, deg_S['value'][0], deg_E['value'][0] )
    screen.blit( msrc['file'], dst, ( xy[0]-xsize//2, xy[1]-ysize//2, xsize, ysize))
    # put cross hair at center of blit image
    center = [sub_screen[0]+S1SZ[0]//2, sub_screen[1]+S1SZ[1]//2]
    p1 = [center[0], center[1]-10]
    p2 = [center[0], center[1]+10]
    p3 = [center[0]+10, center[1]]
    p4 = [center[0]-10, center[1]]
    pygame.draw.line( screen,GREEN_HI,p1, p2,2 )
    pygame.draw.line( screen,GREEN_HI,p3, p4,2 )
#-------------------------------------------------------------------------------
def do_thrust( xcon, ev_timer, time, thrust, stop_button):
    # for now just turn off timer at zero
    print('Doing Thrust for ',xcon.xctls[time]['value'][0],' seconds')
#-------------------------------------------------------------------------------
pygame.init()
pygame.joystick.init()  # Initialize the joysticks.
joysticks = [pygame.joystick.Joystick(x) \
            for x in range(pygame.joystick.get_count())]
if len(joysticks)==0:
    JOY = False
    print('No joysticks. Building simulated joystick')
    #build_sim_joy()
else:
    JOY = True

scr_size= (1760,990)   # Set the width and height of the screen (width, height).
screen = pygame.display.set_mode(scr_size)
pygame.display.set_caption("  Gateway 2024 Controls")

pygame.display.set_icon(pygame_icon)
swide=scr_size[0]

#--------------------  build up the controls 'xcon' and 'PDF' -------------------

xcon = Xcontrol('Gateway24', screen, JOY)  # Note: xcon items are always active in display
print('running xcontrols version',xcon.version)
Xregister( xcon,  [] , always=True) # Xregistering causes update_all & display_all
                                     # 2nd list is MOUSEB activation (see PFD)

xcon.make( 'auto_man','MOUSEB', [-3], [5,5]) # mouse buttons, neg means horizontal
xcon.mouseb_caption( 'auto_man',  0, 'Auto')
xcon.mouseb_caption( 'auto_man',  1, 'Prog')
xcon.mouseb_caption( 'auto_man',  2, 'Manual')
xcon.mouseb_pressed( 'auto_man',  2, True)   # set a button on like this

xcon.make( 'left_buttons', 'MOUSEB', [14], [5,65])  #left buttons

xcon.make( 'Flight_controls','MOUSEB', [-2], [335,5])#  right buttons
xcon.mouseb_caption( 'Flight_controls',  0, 'PFD')
xcon.mouseb_pressed( 'Flight_controls',  0, True)
xcon.mouseb_caption( 'Flight_controls',  1, 'Dock')


xcon.make( 'Sim_parms','MOUSEB', [-4], [555,5])#  right buttons
xcon.mouseb_caption( 'Sim_parms',  0, 'Sim')
xcon.mouseb_caption( 'Sim_parms',  1, 'RealTm')
xcon.mouseb_pressed( 'Sim_parms',  1, True)
xcon.mouseb_caption( 'Sim_parms',  2, 'sec=Min')
xcon.mouseb_caption( 'Sim_parms',  3, 'sec=Hour')

xcon.make('time_rate','SET_DATA','RealTm', 1 )  # set time_rate parameter via flag
xcon.make('time_rate','SET_DATA','sec=Min', 60 )
xcon.make('time_rate','SET_DATA','sec=Hour', 3600 )

#------------------------------------------------------------------------------
PFD = Xcontrol('Primary Flight Display', screen, JOY)
Xregister( PFD,  ['Flight_controls',  0] ) # register PDF as button 0 True

PFD.make( 'Screen2_buttons','MOUSEB', [-4], [swide-4*110,5])#  right buttons
PFD.mouseb_caption( 'Screen2_buttons',  0, 'Mission')
PFD.mouseb_pressed( 'Screen2_buttons',  0, True)
PFD.mouseb_caption( 'Screen2_buttons',  1, 'Map_S1')
PFD.mouseb_caption( 'Screen2_buttons',  2, 'Engs')
PFD.mouseb_caption( 'Screen2_buttons',  3, 'Batts')

PFD.make( 'ev_stst','MOUSEB', [-2], [270,820])#  right buttons
PFD.mouseb_caption( 'ev_stst',  0, 'Start')
PFD.mouseb_caption( 'ev_stst',  1, 'Stop')
PFD.mouseb_pressed( 'ev_stst',  1, True)

PFD.make( 'ev_units','MOUSEB', [2], [580,740])#  right buttons
PFD.mouseb_caption( 'ev_units',  0, 'Ev_secs')
PFD.mouseb_caption( 'ev_units',  1, 'Ev_mins')
PFD.mouseb_pressed( 'ev_units',  0, True)

PFD.make( 'Misson_buttons','MOUSEB', [14], [swide-105,65])#  right buttons
PFD.mouseb_caption( 'Misson_buttons',  0, 'TRANSIT')
PFD.mouseb_caption( 'Misson_buttons',  1, 'NRI')
PFD.mouseb_caption( 'Misson_buttons',  2, 'GWAY')
PFD.mouseb_caption( 'Misson_buttons',  3, 'DESCENT')
PFD.mouseb_caption( 'Misson_buttons',  4, 'TARGETS')
PFD.mouseb_caption( 'Misson_buttons',  5, 'TRACK')
PFD.mouseb_caption( 'Misson_buttons',  6, 'LAND_1a')
PFD.mouseb_caption( 'Misson_buttons',  7, 'LAND')
PFD.mouseb_caption( 'Misson_buttons',  8, 'SITE1')
PFD.mouseb_caption( 'Misson_buttons',  9, 'HLS')
PFD.mouseb_caption( 'Misson_buttons', 10, 'ICE')
PFD.mouseb_caption( 'Misson_buttons', 11, 'ASCENT')
PFD.mouseb_caption( 'Misson_buttons', 12, 'toEARTH')
PFD.mouseb_caption( 'Misson_buttons', 13, 'XCONs')
PFD.mouseb_pressed( 'Misson_buttons',  13, True)  # start with GWAY NRHO orbit


#mission_flag=False

PFD.make('the_mission','SET_DATA','TRANSIT', m_out ) # set the_mission to filename
PFD.make('the_mission','SET_DATA','NRI', m_nri )
PFD.make('the_mission','SET_DATA','GWAY', m_gway )
PFD.make('the_mission','SET_DATA','DESCENT', m_dsc )
PFD.make('the_mission','SET_DATA','TRACK', m_track )
PFD.make('the_mission','SET_DATA','LAND_1a', m_site_1a )
PFD.make('the_mission','SET_DATA','LAND', m_land )
PFD.make('the_mission','SET_DATA','SITE1', m_site1 )
PFD.make('the_mission','SET_DATA','HLS', m_hls )
PFD.make('the_mission','SET_DATA','TARGETS', m_target )
PFD.make('the_mission','SET_DATA','ICE', m_ice )
PFD.make('the_mission','SET_DATA','ASCENT', m_asc )
PFD.make('the_mission','SET_DATA','toEARTH', m_ret )
PFD.make('the_mission','SET_DATA','XCONs', m_xcontrols )
the_mission = m_out

# if Mission flag, will run screen.blit( parameter['the_mission'], sub_screen))
PFD.make('mission_action','SET_ACTION','Mission',
            partial( do_blit, flag='the_mission', pos=sub_screen))

PFD.make('Engine_plot','SET_DATA','Engs', Engs )
PFD.make('Eng_plot_action','SET_ACTION','Engs',
            partial( do_blit, flag='Engine_plot', pos=sub_screen))

PFD.make('Battery_plot','SET_DATA','Batts', Batts )
PFD.make('Bat_plot_action','SET_ACTION','Batts',
            partial( do_blit, flag='Battery_plot', pos=sub_screen))

xcon.make('Dock_plot','SET_DATA','Dock', Doc )
xcon.make('Doc_plot_action','SET_ACTION','Dock',
            partial( do_blit, flag='Dock_plot', pos=(200,150)))

PFD.make( 'axis0', 'AXIS', [0], [930,860])  #left right (x axis)
PFD.label_top( 'axis0',  'Axis0')
PFD.rate( 'axis0',  1000)  # rate of change allowed per second

PFD.make( 'axis1', 'AXIS', [1], [1130,860])  #left right (y axis)
PFD.label_top( 'axis1',  'Axis1')
PFD.rate( 'axis1',  1000)  # rate of change allowed per second

PFD.make( 'date_time', 'TIME', [55], [666,60])   # place a TIME display

PFD.make( 'XYvAng', 'PARAM', [90], [])
PFD.make( 'ZvAng', 'PARAM', [0], [])
PFD.make( 'vel_state', 'GAGE_R1', ['XYvAng', 'ZvAng'], [420, 600])
PFD.label_top( 'vel_state', 'Yaw_Vel')

PFD.make( 'xcon', 'AXIS', [2], [1100,1060])
PFD.label_top( 'xcon',  'Joystick')
PFD.rate( 'xcon',  1000)  # rate of change allowed per second
PFD.translate('xcon',[-1,-.05,.05,1],[2000,1000,1000,-1])

PFD.make( 'doTH', 'BSW', [6], [145,780])
PFD.label_top( 'doTH',  'doThrust')
PFD.label_bot( 'doTH',  'OFF')

PFD.make( 'retPro', 'BSW', [30], [145,910])
PFD.label_top( 'retPro',  'RetGrade')
PFD.label_bot( 'retPro',  'ProGrade')

xcon.make( 's2con', 'SW2', [8,9], [720,780])
xcon.label_top( 's2con',  'doPitch')
xcon.label_bot( 's2con',  'OFF')

xcon.make( 's3con', 'SW2', [10,11], [800,780])
xcon.label_top( 's3con',  'doRoll')
xcon.label_bot( 's3con',  'OFF')

xcon.make( 's4con', 'SW2', [12,13], [890,780])
xcon.label_top( 's4con',  'doYaw')
xcon.label_bot( 's4con',  'OFF')

PFD.make( 'axis4', 'AXIS', [4], [-1,-1])
PFD.label_top( 'axis4',  'Axis4')
PFD.rate( 'axis4',  1000)  # rate of change allowed per second

PFD.make( 'Thrus', 'SLIDER_Y', ['mouse'], [125, 181])
PFD.grid( 'Thrus', [0,100,1])
PFD.setval( 'Thrus', 0)

PFD.make( 'axis6', 'AXIS', [6], [1330,860])  #left right (y axis)
PFD.label_top( 'axis6',  'Axis6')
PFD.rate( 'axis6',  500)  # rate of change allowed per second
PFD.translate('axis6',[-1,0,1],[0,570,1000] )

#PFD.make( 'velocity', 'GAGE_Y', ['axis6','axis4'], [650,340])
PFD.make( 'velocity', 'GAGE_Y', ['Thrus'], [580,340])
PFD.grid( 'velocity', 10)
PFD.label_top( 'velocity', 'Velocity')
PFD.targets('velocity', [1000,None] )

#PFD.make( '_pitch', 'PARAM', [0], [])
#PFD.make( 'pitch_gage', 'GAGE_YS', ['_pitch'], [350,340]) # gage displayed from param
PFD.make( '_Pitch', 'SLIDER_Y', ['mouse'], [710, 181])  # slider mouse base source
PFD.grid( '_Pitch', [0,360,1])
PFD.setval( '_Pitch', 0)

PFD.make( 'pitch_gage', 'GAGE_YS', ['_Pitch'], [350,340]) # gage from another source
PFD.grid( 'pitch_gage', 5)
PFD.rate( 'pitch_gage',  500)  # rate of change allowed per second
PFD.colors( 'pitch_gage', [PURPLE,GRAY,BLUE,YELLOW,GREEN])
#PFD.label_top( 'pitch_gage', 'Velocity')
PFD.targets('pitch_gage', [90,None] )

PFD.make( 'deltaV', 'PARAM', [0], [])

PFD.make( 'testx', 'GAGE_X', ['deltaV','axis6'], [435, 660])
PFD.grid( 'testx', 500)
PFD.label_top( 'testx', 'TESTX')

PFD.make( 'Roll_Rate', 'PARAM', [0], [])
PFD.make( 'roll_rate', 'GAGE_X', ['Roll_Rate'], [435, 100])
PFD.label_top( 'roll_rate', 'Roll_Rate')

PFD.make( 'Zv', 'PARAM', [77], [])
PFD.make( 'ball_obj', 'GAGE_R2', ['_Yaw','_Roll'], [385, 340])
PFD.rate( 'ball_obj',  500)  # rate of change allowed per second

PFD.make( 'hdot0', 'PARAM', [1250], [])
PFD.make( 'hdot1', 'AXIS', [3], [1360,770])  #left right (y axis)
PFD.translate('hdot1',[-1,0,1],[-1200,0,1200] )
PFD.make( 'hdot2', 'PARAM', [20], [])
PFD.make( 'hdotx', 'HDOT', ['hdot0','hdot1','hdot2'], [790, 864])
PFD.targets('hdotx', [1000, 20, 33] )

xcon.make( 'map_type', 'BSW', [2], [1030,910])
xcon.label_top( 'map_type',  'Map_5mmp')
xcon.label_bot( 'map_type',  'Map_10mmp')

xcon.make( 'b15', 'BSW', [15], [1140,910])
xcon.label_top( 'b15',  'Vector')
xcon.label_bot( 'b15',  'Coords')

xcon.make( 'LRate', 'BSW', [3], [1250,910])
xcon.label_top( 'LRate',  'Rate_10')
xcon.label_bot( 'LRate',  'Rate_1')

xcon.make( 'TType', 'BSW', [1], [630,910])
xcon.label_top( 'TType',  'timed_Th')
xcon.label_bot( 'TType',  'off')

xcon.make( 'Flyby', 'BSW', [1], [520,910])
xcon.label_top( 'Flyby',  'Flyby')
xcon.label_bot( 'Flyby',  'off')

PFD.make( 'th_time', 'PARAM', [20], [])
PFD.make( 'Ev_Timer', 'SLIDER_X', ['mouse'], [200, 780])
PFD.grid( 'Ev_Timer', [0,100,1])
PFD.setval( 'Ev_Timer', 50)
PFD.make( 'Timer', 'TIMER', ['Ev_Timer',['ev_stst',0] ],
                [partial( do_thrust, PFD,'Ev_Timer','th_time','Thrus',['ev_stst',1]) ])

PFD.make( '_Roll', 'SLIDER_Y', ['mouse'], [785, 180])
PFD.grid( '_Roll', [0,360,1])
PFD.setval( '_Roll', 90)

PFD.make( '_Yaw', 'SLIDER_Y', ['mouse'], [860, 180])
PFD.grid( '_Yaw', [0,360,1])
PFD.setval( '_Yaw', 90)

PFD.make( 'deg_S', 'MAXIS', [site1[0]], [1385, 900])
PFD.grid( 'deg_S', [0,360,10,.01])
PFD.rate( 'deg_S',  .003)  # rate for MAXIS is how fast the wheel moves gage needle

PFD.make( 'deg_E', 'MAXIS', [site1[1]], [1540, 900])
PFD.grid( 'deg_E', [0,360,10,.01])
PFD.rate( 'deg_E',  .2)  # rate for MAXIS is how fast the wheel moves gage needle

PFD.make('moonplot_action','SET_ACTION','Map_S1',
            partial( blit_moon_map, msrc=moon, dst=sub_screen,
                  deg_S=PFD.xctls['deg_S'], deg_E=PFD.xctls['deg_E'],
                  xsize=S1SZ[0], ysize=S1SZ[1]))

PFD.make( 'text_in', 'TXIN', [700], [945, 800])
PFD.make( 'text_out', 'TXOUT', ['text_in'], [945, 768])

#-------------------------------------------------------------

DOCK = Xcontrol('Docking Controls', screen, JOY)
Xregister( DOCK,  ['Flight_controls',  1] ) # register Dock button 1 True

DOCK.make( 'Dock_buttons','MOUSEB', [-3], [swide-4*110,5])#  right buttons
DOCK.mouseb_caption( 'Dock_buttons',  0, 'NRHO')
DOCK.mouseb_caption( 'Dock_buttons',  1, 'Engs')
DOCK.mouseb_caption( 'Dock_buttons',  2, 'Batts')
DOCK.mouseb_pressed( 'Dock_buttons',  0, True)  # start with GWAY NRHO orbit

DOCK.make('GW_Orbit','SET_DATA','NRHO', nrho)
DOCK.make('NRHO_plot','SET_ACTION','NRHO',
            partial( do_blit, flag='GW_Orbit', pos=sub_screen))

DOCK.make('Engine_plot','SET_DATA','Engs', Engs )
DOCK.make('Eng_plot_action','SET_ACTION','Engs',
            partial( do_blit, flag='Engine_plot', pos=sub_screen))

DOCK.make('Battery_plot','SET_DATA','Batts', Batts )
DOCK.make('Bat_plot_action','SET_ACTION','Batts',
            partial( do_blit, flag='Battery_plot', pos=sub_screen))

DOCK.make( 'RCS', 'MAXIS', [90], [250, 830])
DOCK.grid( 'RCS', [0,100,5,3])
DOCK.rate( 'RCS',  1)  # rate of change allowed per wheel click
DOCK.setval( 'RCS', 0)

DOCK.make( '_Roll', 'SLIDER_Y', ['mouse'], [785, 181])
DOCK.grid( '_Roll', [0,360,1])
DOCK.setval( '_Roll', 90)

DOCK.make( '_Yaw', 'SLIDER_Y', ['mouse'], [860, 181])
DOCK.grid( '_Yaw', [0,360,1])
DOCK.setval( '_Yaw', 90)

DOCK.make( '_Pitch', 'SLIDER_Y', ['mouse'], [710, 181])  # slider mouse base source
DOCK.grid( '_Pitch', [0,360,1])
DOCK.setval( '_Pitch', 90)

DOCK.make( 'joystick', 'MJOY', ['mouse'], [450, 750])

set_map_center( moon, site1 )

# ------ Loop until the user clicks the close button ----------
done = False
while not done:  # MAIN PROCESSING LOOP
    screen.fill(XBLACK)  # start with a blank screen
    done = process_xcons()  # update and draw the xcon screens
    process_sim( parameter['time_rate'] ) # time_rate is seconds per step
    pygame.display.update()
    pygame.display.flip()  # update screens with what was drawn

pygame.quit()