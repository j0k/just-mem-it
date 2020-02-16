from datetime import datetime
from dataclasses_json import dataclass_json

import time
import json

import tkinter as tk
import tkinter.ttk as ttk

from tkinter.ttk import Frame, Label
#from tkinter import ttk

from tkinter import Tk, BOTH, Listbox, StringVar, END, LEFT, HORIZONTAL, N
from tkinter import Button, Entry
from tkinter import scrolledtext, Scrollbar
from tkinter.ttk import Progressbar

import tkinter as tk

from dacite import from_dict

from . import item as Mem
from . import util as MemUtil
from . import config

class Example(Frame):
    def __init__(self, log, db, scales):
        super().__init__()
        self.log = log
        self.lb = None
        self.db     = db

        self.scales = {}
        for scale in scales:
            self.scales[scale["title"]] = scale

        self.items = []
        self.counter = 0
        self.onRemind = False
        self.lastSelected = -1

        self.initUI()


    def addMemClicked(self):
        self.log.info("add mem")
        title = self.txtTitle.get()
        desc  = self.txtDesc.get("0.0", END)
        hint  = self.txtHint.get("0.0", END)
        scale = self.txtScale.get()

        mem = Mem.Item(title=title, description=desc, hint=hint, scale=scale)
        print(mem)

        self.addMem(mem)

    def delMemClicked(self):
        select = self.lb.curselection()

        if len(select) > 0:
            select = self.lb.curselection()[0]
        else:
            return

        if select >= 0:
            self.lb.delete(select, select)
            del self.items[select]

        self.log.info("selection: {}".format(self.lb.curselection()))

    def addMem(self, mem):
        self.items.append(mem)

        self.lb.insert(END, mem.title)
        if mem.paused == True:
            self.lb.itemconfig(END, {'bg':'red'})
        else:
            self.lb.itemconfig(END, {'bg':'green'})

    def initUI(self):
        tab_control = ttk.Notebook(self)
        tabAdd  = ttk.Frame(tab_control)
        tabList = ttk.Frame(tab_control)

        tab_control.add(tabAdd,  text='Add smth to mem')
        tab_control.add(tabList, text='List')

        lbl1 = Label(tabAdd, text= 'Welcome to memorization app')
        btn = Button(tabAdd, text="+", command=self.addMemClicked)

        txtTitle = Entry(tabAdd, text="txt", width=30, state='normal')
        txtTitle.insert(0, "skill title")

        txtDesc  = scrolledtext.ScrolledText(tabAdd, width=20,height=10)
        txtDesc.insert(0.0, "description")

        txtHint  = scrolledtext.ScrolledText(tabAdd, width=20,height=3)
        txtHint.insert(0.0, "hint")

        txtScale = ttk.Combobox(tabAdd, width=27, values=list(self.scales.keys()), state="readonly")
        txtScale.current(0)

        self.txtTitle = txtTitle
        self.txtDesc  = txtDesc
        self.txtScale = txtScale
        self.txtHint  = txtHint

        lbl1.grid(column=0, row=0)
        btn.grid(column=0, row=1)

        txtTitle.grid(column=1, row=1)
        txtScale.grid(column=1, row=2)
        txtDesc.grid(column=1,row=3)
        txtHint.grid(column=1,row=4)

        tab_control.pack(expand=1, fill='both')
        self.pack(fill=BOTH, expand=1)

        btnDel = Button(tabList,  text="-",    command = self.delMemClicked)
        btnSave = Button(tabList, text="save", command = self.onSave)
        btnRestart = Button(tabList, text="restart", command = lambda : True)
        lb = Listbox(tabList)

        self.varDesc = StringVar()
        lbTxtDesc = scrolledtext.ScrolledText(tabList,width=20,height=10)
        lbTxtHint = scrolledtext.ScrolledText(tabList,width=20,height=10)

        lbTxtScale = ttk.Combobox(tabList, width=27, values=list(self.scales.keys()), state="readonly")
        lbTxtScale.current(0)

        self.lb = lb
        self.lbTxtDesc = lbTxtDesc
        self.lbTxtHint = lbTxtHint
        self.lbTxtScale = lbTxtScale

        scrollbar = Scrollbar(tabList, orient="vertical")
        scrollbar.config(command=lb.yview)
        #scrollbar.pack(side="right", fill="y")
        btnDel.grid(column=0, row=0)
        btnSave.grid(column=1, row=0)
        # btnRestart.grid(column=1, row=0)

        lbTxtScale.grid(column=2, row=0)
        scrollbar.grid(column=0, row=1, sticky='ns')

        lb.config(yscrollcommand=scrollbar.set)

        for item in self.db:
            mem = from_dict(Mem.Item, item)
            self.addMem(mem)



        lb.bind("<<ListboxSelect>>", self.onSelect)

        #lb.pack(pady=15)
        lb.grid(column=1, row=1)
        #lbTxtDesc.pack(pady=15)
        lbTxtDesc.grid(column=2, row=1)
        lbTxtHint.grid(column=3, row=1)


        sRed = ttk.Style()
        sRed.theme_use('clam')
        sRed.configure("red.Horizontal.TProgressbar", foreground='red', background='red')

        sGreen = ttk.Style()
        sGreen.theme_use('clam')
        sGreen.configure("green.Horizontal.TProgressbar", foreground='green', background='green')

        self.var = StringVar()
        self.varMemCount = StringVar()
        self.varNextTime = StringVar()

        self.btnPlay  = Button(self, text=">", command=self.playMem, state="disabled")
        self.btnPause = Button(self, text="||", command=self.pauseMem, state="disabled")
        self.btnRestart = Button(self, text="R", command=self.restartMem, state="normal")

        self.btnPlay.pack(side=LEFT)
        self.btnPause.pack(side=LEFT)
        self.btnRestart.pack(side=LEFT)

        self.label = Label(self, text=0, textvariable=self.var)
        self.label.pack(side=LEFT)

        self.lMemCount = Label(self, text=0, textvariable=self.varMemCount)
        self.lMemCount.pack(side=LEFT)

        self.progress = Progressbar(self, style="red.Horizontal.TProgressbar", orient=HORIZONTAL, length=100, mode='determinate')
        self.progress['value'] = 0
        self.progress.pack(side = LEFT)

        self.timeProgress = Progressbar(self, style="green.Horizontal.TProgressbar", orient=HORIZONTAL, length=100, mode='determinate')
        self.timeProgress['value'] = 0
        self.timeProgress.pack(side = LEFT)

        self.labelNextTime = Label(self, text=0, textvariable=self.varNextTime)
        self.labelNextTime.pack(side=LEFT)


    def onSelect(self, val):
        sender = val.widget
        #print(sender, val)
        idx = sender.curselection()

        if len(idx) == 0:
            return
        #print(idx)
        value = sender.get(idx)

        self.var.set(value)
        self.log.info("select {} - {}".format(idx, value))
        self.lastSelected = idx[0]

        item = self.items[idx[0]]
        if item.paused:
            self.btnPause.config(state="disabled")
            self.btnPlay.config(state="normal")
        else:
            self.btnPause.config(state="normal")
            self.btnPlay.config(state="disabled")

        self.lbTxtDesc.delete(0.0, END)
        self.lbTxtDesc.insert(0.0, self.items[idx[0]].description)

        self.lbTxtHint.delete(0.0, END)
        self.lbTxtHint.insert(0.0, self.items[idx[0]].hint)

        if len(item.nextTimes) > 0:
            nextTime    = item.nextTimes[-1][1]
            strNextTime = str(datetime.fromtimestamp(nextTime))
            self.varNextTime.set(strNextTime)

        scales  = list(self.scales.keys())
        listIdx = 0
        if item.scale in scales:
            listIdx = scales.index(item.scale)

        scale = self.scales[item.scale]

        self.lbTxtScale.current(listIdx)

        memDoneCount  = MemUtil.scaleMemDoneCount(scale)
        self.varMemCount.set("({}/{})".format(len(item.reminders), memDoneCount))

        if memDoneCount >= 0 :
            progress = 100 * len(item.reminders) / memDoneCount
            progress = min(progress, 100)
            self.progress['value'] = int(progress)
            self.update_idletasks()

    def onSave(self):
        if self.lastSelected >= 0:
            itemIdx = self.lastSelected
            item    = self.items[itemIdx]

            item.description  = self.lbTxtDesc.get("0.0", END)
            item.hint         = self.lbTxtHint.get("0.0", END)
            item.scale        = self.lbTxtScale.get()

            self.items[self.lastSelected] = item
            self.saveAllItems()


    def playMem(self, select = None):
        if select == None:
            select = self.lb.curselection()[0]
        select = self.lb.curselection()[0]
        item = self.items[select]

        item.paused = False
        self.lb.itemconfig(select, {'bg':'green'})
        self.btnPause.config(state="normal")
        self.btnPlay.config(state="disabled")

        self.log.info("play")

    def pauseMem(self, select = None):
        if select == None:
            select = self.lb.curselection()[0]
        item = self.items[select]

        item.paused = True
        self.lb.itemconfig(select, {'bg':'red'})
        self.btnPause.config(state="disabled")
        self.btnPlay.config(state="normal")
        self.log.info("pause")

    def restartMem(self, select = None):
        if select == None:
            select = self.lb.curselection()[0]
        item = self.items[select]

        MsgBox = tk.messagebox.askquestion ('Restart skill: ' + item.title, "Do you really want to restart this skill?\n" + item.title + "\n" + item.description , icon = 'warning')
        if MsgBox == 'yes':
            item.reminders = []
            item.nextTimes = []
            item.lastIntervals = []
            self.saveAllItems()
        else:
            pass


    def remind(self, item, idx, reminders):
        self.onRemind = True
        res = {}
        def callbackSkip():
            self.onRemind = False
            self.pauseMem(idx)
            self.log.info('remind =no')

        def callbackOkay():
            self.onRemind = False
            item.reminders.append(time.time())
            self.log.info('remind =yes')
            self.saveAllItems()

        MsgBox = Mbox(item.title, item.description, item.hint, callbackOkay, callbackSkip, res)

    def saveAllItems(self):
        self.log.info("save file")
        progressFile = config.progressFile
        with open(progressFile, 'w') as outfile:
            jsonItems = [item.to_dict() for item in self.items]
            json.dump(jsonItems, outfile, indent=2)



# https://stackoverflow.com/questions/10057672/correct-way-to-implement-a-custom-popup-tkinter-dialog-box
class Mbox(object):
    root = None

    def __init__(self, title, desc, hint, callbackOkay, callbackSkip, result, dict_key=None):
        """
        msg = <str> the message to be displayed
        dict_key = <sequence> (dictionary, key) to associate with user input
        (providing a sequence for dict_key creates an entry for user input)
        """
        tki = tk
        self.result = result
        self.top = tki.Toplevel(Mbox.root)

        frm = tki.Frame(self.top, borderwidth=4, relief='ridge')
        frm.pack(fill='both', expand=True)

        labelT = tki.Label(frm, text=title)
        labelT.pack(padx=4, pady=4)

        txtDesc  = scrolledtext.ScrolledText(frm, width=20,height=10)
        txtDesc.insert(0.0, desc)
        txtDesc.pack(padx=4, pady=4)

        txtHint  = scrolledtext.ScrolledText(frm, width=20,height=3)
        txtHint.pack(padx=4, pady=4)


        caller_wants_an_entry = dict_key is not None

        if caller_wants_an_entry:
            self.entry = tki.Entry(frm)
            self.entry.pack(pady=4)

            b_submit = tki.Button(frm, text='Submit')
            b_submit['command'] = lambda: self.entry_to_dict(dict_key)
            b_submit.pack()

        def hintPressed():
            txtHint.delete(0.0, END)
            txtHint.insert(0.0, hint)

        b_hint = tki.Button(frm, text='Show Hint')
        b_hint['command'] = hintPressed
        b_hint.pack(padx=4, pady=4)

        def skipPressed():
            self.result = {"result": "skip"}
            callbackSkip()
            self.top.destroy()


        b_skip = tki.Button(frm, text='Skip')
        b_skip['command'] = skipPressed
        b_skip.pack(padx=4, pady=4)

        def okayPressed():
            self.result = {"result": "okay"}
            callbackOkay();
            self.top.destroy()

        b_okay = tki.Button(frm, text='Okay')
        b_okay['command'] = okayPressed
        b_okay.pack(padx=4, pady=4)

    def entry_to_dict(self, dict_key):
        data = self.entry.get()
        if data:
            d, key = dict_key
            d[key] = data
            self.top.destroy()
