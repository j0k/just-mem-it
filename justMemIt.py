from tkinter import Tk
from tkinter import messagebox

import json
import tkinter as tk
import time
import logging

from memcore import item as Mem
from memcore import mainwin as MainWin
from memcore import util as MemUtil
from memcore import config as MemConfig

import ipdb

from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        win.root.destroy()
        win.rt.stop()


memProgressFile = MemConfig.progressFile
db = []


logger = logging.getLogger('JMI')

#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.setLevel(logging.INFO)

try:
    f  = open(MemConfig.progressFile, "r")
    logger.info("{} - file loaded".format(MemConfig.progressFile))
    db = json.load(f)
    f.close()
    # Do something with the file
except IOError:
    logger.error("{} - file not accessible".format(MemConfig.progressFile))
    db = json.load(open("mem/all.json", "r"))
finally:
    pass

scalesDB = json.load(open("mem/scales.json", "r"))
logger.info(db)

def scanMems(app):
    if app.onRemind:
        return

    selected = app.lb.curselection()
    select = -1
    if len(selected) > 0:
        select = app.lb.curselection()[0]

    for idx, item in enumerate(app.items):
        if app.onRemind:
            return

        if item.paused:
            continue

        cur = len(item.reminders)

        lastInterval  = item.lastIntervals[-1] if len(item.lastIntervals) > 0 else 0
        nextInterval  = 0
        nextTime      = time.time() + nextInterval
        if cur == len(item.nextTimes):
            scale = app.scales[item.scale]
            nextInterval  = MemUtil.onScale(scale, [lastInterval, cur])
            item.lastIntervals.append(nextInterval)
            # print("(%s) NI: %s" % (item.title,nextInterval))

            nextTime      = time.time() + nextInterval
            item.nextTimes.append([time.time(), nextTime]) # [whenAdded, whenExecute]

        whenAdded, whenExecute = item.nextTimes[-1]
        deltaMax = whenExecute - whenAdded
        deltaCur = time.time() - whenAdded
        reminder = 0 if len(item.reminders) == 0 else item.reminders[-1]

        if time.time() > whenExecute:
            logger.info("its time for skill %s %s" % (item.title, cur))
            app.remind(item, idx, item.reminders)
        else:
            # print(idx,select,int(100 *  deltaCur/deltaMax))
            if idx == select:
                app.timeProgress['value'] = int(100 * deltaCur/deltaMax)
                app.update_idletasks()

logger.info("starting...")

class Win:
    def __init__(self, log, on_closing):
        self.root = Tk()
        self.log  = log
        self.root.title("Just mem it")
        self.root.geometry("500x350+300+300")
        self.root.protocol("WM_DELETE_WINDOW", on_closing)

    def setDB(self, db):
        self.ex = MainWin.Example(self.log, db, scalesDB)
        self.rt = RepeatedTimer(1, scanMems, self.ex) # it auto-starts, no need of rt.start()


win = Win(logger, on_closing)

def main():
    win.setDB(db)
    MainWin.Mbox.root = win.root

    win.root.mainloop()

if __name__ == '__main__':
    main()
