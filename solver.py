import numpy as np
from grabscreen import grab_screen
import cv2
import time
import win32gui
import os
import glob
from directkeys import TapKey, W, A, S, D, TAB, ENTER

toplist, winlist = [], []
def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
win32gui.EnumWindows(enum_cb, toplist)

gta =[ hwnd for hwnd, title in winlist if 'grand theft' in title.lower()]

print("Window:", gta)
hwnd = gta[0]
time.sleep(2)
win32gui.SetForegroundWindow(hwnd)

bbox = win32gui.GetWindowRect(hwnd)

comppool = []

def load_solutions():
    img_dir='sol'
    data_path = os.path.join(img_dir,'*g')
    files = glob.glob(data_path)

    for file in files:
            comppool.append(cv2.imread(file))
            

def compare_to_sol(img):
    maxval = 0
    for sol in comppool:
        res = cv2.matchTemplate(img,sol,cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > maxval:
            maxval = max_val
    return maxval

def selectSol(x,y):
    print(x,y)
    for i in range(x):
        TapKey(D)
        time.sleep(.02);
    for i in range(y):
        TapKey(S)
        time.sleep(.02);
    TapKey(ENTER)
    time.sleep(.1)
    for i in range(x):
        TapKey(A)
        time.sleep(.02);
    for i in range(y):
        TapKey(W)
        time.sleep(.02);


MIN_SIMILARITY = 0.75   
def screen_record(): 
    while(True):
        printscreen =  np.array(grab_screen(bbox))
        #cv2.imwrite('ss.png', printscreen)
        printscreen =  cv2.cvtColor(printscreen, cv2.COLOR_BGR2GRAY)

        # pull component list from image
        components = [[None]*4, [None]*4]
        maxSim = 0
        for i in range(2):
            for j in range(4):
                # Adjust to be percentages of resolution
                x = 480 + i * (625-480)
                y = 277 + j * (421-277)
                components[i][j] = cv2.cvtColor(printscreen[y:y+107, x:x+107], cv2.COLOR_BGR2RGB)
                similarity = compare_to_sol(components[i][j])
                if similarity > MIN_SIMILARITY:
                    selectSol(i, j)
                if similarity > maxSim:
                    maxSim = similarity
        if maxSim > 0.75:
            TapKey(TAB)
            time.sleep(4.5)
            maxSim = 0
        else:
            print('No match found. Maxsim:', maxSim)
        time.sleep(.250)

        #debugging, show screenshot
        #cv2.imshow('window2',printscreen)
        #if cv2.waitKey(25) & 0xFF == ord('q'):
        #    cv2.destroyAllWindows()
        #    break

print("Started Watching...")
load_solutions()
screen_record()
