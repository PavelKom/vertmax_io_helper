import pygubu  # pip install pygubu
import tkinter.ttk as ttk
import tkinter as tk
from Xlib.protocol import event
from Xlib import display, X, XK
import Xlib
from pathlib import Path
import json, sys, datetime, os, webbrowser
from configparser import ConfigParser

# Useless cause PLC2.exe not support copy-paste
# import pyperclip    #pip install pyperclip


def get_external_path(rel):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return os.path.join(application_path, rel)


def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    else:
        return os.path.join(os.path.abspath("."), relative)


PROJECT_PATH = resource_path("")
UI_PATH = resource_path("vioh_ui.ui")
CFG_PATH = get_external_path("cfg.ini")
IO_PATH = "C:/WNC/home/d_xnc/dati/data/"

special_X_keysyms = {
    ' ': "space",  # 65
    '_': "underscore",
}

d = display.Display()
dr = d.screen().root
plc_win = None
plc_widgets = list()

i_cfg = ConfigParser() # OEM Inputs
o_cfg = ConfigParser() # OEM Outputs
p_cfg = ConfigParser() # Config
LOC_HASH = dict()
i_cfg_sec = None
o_cfg_sec = None
c_path = Path(CFG_PATH)
er = 0
if not c_path.is_file():
    p_cfg.add_section('Settings')
    p_cfg.set('Settings', 'i_file', IO_PATH + "oem_msd_in.dat.ini")
    p_cfg.set('Settings', 'o_file', IO_PATH + "oem_msd_out.dat.ini")
    p_cfg.set('Settings', 'io_file', "io_data.json")
    p_cfg.set('Settings', 'plc2_cmd', "")
    f = c_path.open("w")
    p_cfg.write(f)
    f.close()
else:
    p_cfg.read(CFG_PATH)
if Path(p_cfg.get('Settings', 'i_file')).is_file():
    i_cfg.read(p_cfg.get('Settings', 'i_file'))
    i_cfg_sec = i_cfg['MSD_IN{0}']
else:
    er |= 1
if Path(p_cfg.get('Settings', 'o_file')).is_file():
    o_cfg.read(p_cfg.get('Settings', 'o_file'))
    o_cfg_sec = o_cfg['MSD_OUT{0}']
else:
    er |= 2
if er == 0:
    DUMP_PATH = get_external_path(p_cfg.get('Settings', 'io_file'))
    d_path = Path(DUMP_PATH)
        
    if not d_path.is_file():
        dump_dict = dict()
        dump_dict["meta"] = {
            "Creation data": str(datetime.datetime.now())
        }
        dump_dict["locations"] = [
            "0.UNKNOWN",
            "1.FRONT HEAD SPINDLE",
            "2.REAR HEAD SPINDLE"]
        dump_dict["inputs"] = dict()
        dump_dict["outputs"] = dict()

        for key in i_cfg_sec:
            dump_dict["inputs"][key] = {
                "type": "input",
                "desc": "",
                "location": 0,
                "port": i_cfg_sec[key]}
        for key in o_cfg_sec:
            dump_dict["outputs"][key] = {
                "type": "output",
                "desc": "",
                "location": 0,
                "port": o_cfg_sec[key]}
        with open(p_cfg.get('Settings', 'io_file'), "w") as f:
            json.dump(dump_dict, f, indent="\t")
            f.close()
    with open(DUMP_PATH, "r", encoding='utf-8') as f:
        f_dump = json.load(f)
        f.close()
        LOC_HASH[''] = 0
        for i, key in enumerate(f_dump["locations"]):
            LOC_HASH[key] = i

TK_VARS = dict()


def loc_change(var, index, mode):
    print(var, TK_VARS[var].get(), LOC_HASH[TK_VARS[var].get()], index, mode)


def get_location(loc):
    if loc in ("", 0):
        return 0
    return loc


def get_keysym(ch):
    keysym = Xlib.XK.string_to_keysym(ch)
    if keysym == 0:
        keysym = Xlib.XK.string_to_keysym(special_X_keysyms[ch])
    return keysym


def check_plc():
    global plc_win
    if plc_win is not None:
        try:
            plc_win.get_wm_name()
            TK_VARS["var_plc"].set("PLC2 LOADED")
            return True
        except BaseException:
            plc_win = None
            pass
    for c in dr.query_tree().children:
        if c.get_wm_name() == "PLC2":
            plc_win = c
            get_plc_widget(c)
            TK_VARS["var_plc"].set("PLC2 LOADED")
            return True
    TK_VARS["var_plc"].set("PLC2 NOT LOADED")
    return False


def get_plc_widget(w, root=True):
    global curr_widget_id, curr_widget, plc_widgets
    if root:
        plc_widgets.clear()
    for i, c in enumerate(w.query_tree().children):
        if str(type(c)) == "<class 'Xlib.display.Window'>":
            if len(w.query_tree().children) == 34:
                if i % 2 == 1 and i >= 3:
                    plc_widgets.insert(0, c)
            get_plc_widget(c, False)


def print_into_plc(msg="", post=False, clear=False):
    if not check_plc():
        return
    global plc_win, plc_widgets
    if len(plc_widgets) == 0:
        return
    send_string(plc_widgets[TK_VARS["var_widget_id"].get() - 1], msg, clear)
    if post:
        v = TK_VARS["var_widget_id"].get() + 1
        if v > 16:
            v -= 16
        TK_VARS["var_widget_id"].set(v)


def short_press(window, data=None, is_mouse=False):
    if is_mouse:
        window.send_event(event.ButtonPress(
            detail=X.Button1,
            root=window, root_x=100, root_y=0,
            window=window, event_x=100, event_y=0,
            same_screen=1, state=0,
            time=X.CurrentTime, child=0
        ))
        window.send_event(event.ButtonRelease(
            detail=X.Button1,
            root=window, root_x=100, root_y=0,
            window=window, event_x=100, event_y=0,
            same_screen=1, state=0,
            time=X.CurrentTime, child=0
        ))
    else:
        # window.send_event(event.KeyPress(
        #    detail=36 if data is None else data,
        #    root=window, root_x=100, root_y=0,
        #    window=window, event_x=100, event_y=0,
        #    same_screen=1, state=0,
        #    time=X.CurrentTime, child=0
        #    ))
        # window.send_event(event.KeyRelease(
        #    detail=36 if data is None else data,
        #    root=window, root_x=100, root_y=0,
        #    window=window, event_x=100, event_y=0,
        #    same_screen=1, state=0,
        #    time=X.CurrentTime, child=0
        #    ))
        Xlib.ext.xtest.fake_input(window, Xlib.X.KeyPress,
                                  36 if data is None else data)
        Xlib.ext.xtest.fake_input(window, Xlib.X.KeyRelease,
                                  36 if data is None else data)


def send_string(window, msg, clear=False):
    global d
    window.send_event(event.FocusIn(
        window=window,
        mode=X.NotifyNormal,
        detail=X.NONE))
    short_press(window=window, is_mouse=True)

    if clear:
        short_press(window, 103)
        for i in range(32):
            short_press(window, 22)
    else:
        for c in msg:
            short_press(window, d.keysym_to_keycode(get_keysym(c)))
    short_press(window=window)


class UI:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        # Get pygubu objects
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(UI_PATH)
        self.mainwindow = builder.get_object('mainwindow', master)
        self.inv_check = builder.get_object('inv_check', master)
        self.i_table = builder.get_object('i_table', master)
        self.o_table = builder.get_object('o_table', master)
        self.widget_id = builder.get_object('widget_id', master)
        self.plc_status = builder.get_object('plc_status', master)
        self.label_author = builder.get_object('label_author', master)
        self.button_clear_slot = builder.get_object('button_clear_slot', master)
        self.locations = builder.get_object('locations', master)
        self.er_i_message = builder.get_object('er_i_message', master)
        self.er_o_message = builder.get_object('er_o_message', master)

        # Bind to functions
        self.label_author.bind("<Button-1>", self.to_github)
        self.button_clear_slot.bind("<Button-1>", self.clear_slot)
        self.plc_status.bind("<Button-1>", self.load_plc)
        self.i_table.bind("<Double-1>", self.i_table_dclick)
        self.o_table.bind("<Double-1>", self.o_table_dclick)

        # Create Variables and link go global field
        self.var_loc = tk.StringVar(name="var_loc")
        self.var_plc = tk.StringVar(name="var_plc")
        self.var_widget_id = tk.IntVar(name="var_widget_id")
        self.var_hide_inv = tk.BooleanVar(name="var_hide_inv")
        TK_VARS["var_loc"] = self.var_loc
        TK_VARS["var_plc"] = self.var_plc
        TK_VARS["var_hide_inv"] = self.var_hide_inv
        TK_VARS["var_widget_id"] = self.var_widget_id

        # Set default values and link to Vars
        self.var_widget_id.set(1)
        self.var_loc.trace_add("write", self.loc_change)
        self.locations["textvariable"] = self.var_loc
        self.plc_status["textvariable"] = self.var_plc
        self.widget_id["textvariable"] = self.var_widget_id
        self.inv_check["variable"] = self.var_hide_inv
        self.var_hide_inv.set(True)
        builder.connect_callbacks(self)
        self.i_table_rows = list()
        self.o_table_rows = list()
        if er == 0:
            self.locations["values"] = f_dump["locations"]
            self.er_i_message.lower(self.i_table)
            self.er_o_message.lower(self.o_table)
            self.init_i_table()
            self.init_o_table()
            self.var_loc.set(f_dump["locations"][0])
            self.change_widget_id()
            self.change_widget_id()
        else:
            if er & 1:
                self.er_i_message["text"] = self.er_i_message["text"] % (p_cfg.get('Settings', 'i_file'))
            if er & 2:
                self.er_o_message["text"] = self.er_o_message["text"] % (p_cfg.get('Settings', 'o_file'))
                
    def run(self):
        self.update()
        self.mainwindow.mainloop()

    def to_github(self, event):
        webbrowser.open_new("https://github.com/PavelKom")

    def clear_slot(self, event):
        print_into_plc("", clear=True)

    def load_plc(self, event):
        if check_plc():
            return
        cmd = p_cfg.get('Settings', 'plc2_cmd')
        os.system(cmd)

    def loc_change(self, var, index, mode):
        global er
        if er != 0:
            return
        self.update_i_table()
        self.update_o_table()

    def init_i_table(self):
        self.i_table['show'] = 'headings'
        self.i_table["columns"] = ('alias', 'desc', 'port')
        self.i_table.heading("alias", text="Alias")
        self.i_table.heading("desc", text="Description")
        self.i_table.heading("port", text="Port")
        # self.i_table.heading("val", text="ЗНАЧ")
        self.i_table.column("#1", stretch=False, width=100)
        self.i_table.column("#2", stretch=True, width=70)
        self.i_table.column("#3", stretch=False, width=100)
        # self.i_table.column("#4", stretch=False, width=50)
        self.update_i_table()

    def init_o_table(self):
        self.o_table['show'] = 'headings'
        self.o_table["columns"] = ('alias', 'desc', 'port')
        self.o_table.heading("alias", text="Alias")
        self.o_table.heading("desc", text="Description")
        self.o_table.heading("port", text="Port")
        # self.o_table.heading("val", text="ЗНАЧ")
        self.o_table.column("#1", stretch=False, width=100)
        self.o_table.column("#2", stretch=True, width=70)
        self.o_table.column("#3", stretch=False, width=100)
        # self.o_table.column("#4", stretch=False, width=50)
        self.update_o_table()

    def update_i_table(self):
        while len(self.i_table_rows) > 0:
            self.i_table.delete(self.i_table_rows.pop())
        i = LOC_HASH[TK_VARS["var_loc"].get()]
        # if i == len(f_dump["locations"]) - 1:
        #    i = -1
        for alias in f_dump["inputs"]:
            if get_location(f_dump["inputs"][alias]['location']) != i:
                continue
            if self.var_hide_inv.get() and i_cfg_sec[alias] == "-1":
                continue
            if i_cfg_sec[alias] == "-1":
                tag = "invalid"
            else:
                tag = "valid"
            self.i_table_rows.append(
                self.i_table.insert(
                    "", tk.END, values=(
                        alias, f_dump["inputs"][alias]['desc'], i_cfg_sec[alias]), tags=(
                        tag,)))
        self.i_table.tag_configure('invalid', background='red')

    def update_o_table(self):
        while len(self.o_table_rows) > 0:
            self.o_table.delete(self.o_table_rows.pop())
        i = LOC_HASH[TK_VARS["var_loc"].get()]
        # if i == len(f_dump["locations"]) - 1:
        #    i = -1
        for alias in f_dump["outputs"]:
            if get_location(f_dump["outputs"][alias]['location']) != i:
                continue
            if self.var_hide_inv.get() and o_cfg_sec[alias] == "-1":
                continue
            if o_cfg_sec[alias] == "-1":
                tag = "invalid"
            else:
                tag = "valid"
            self.o_table_rows.append(
                self.o_table.insert(
                    "", tk.END, values=(
                        alias, f_dump["outputs"][alias]['desc'], o_cfg_sec[alias]), tags=(
                        tag,)))
        self.o_table.tag_configure('invalid', background='red')

    def i_table_dclick(self, event):
        item = self.i_table.selection()[0]
        val = "i" + str(self.i_table.item(item)
                        ["values"][2]) + " " + self.i_table.item(item)["values"][0]
        # pyperclip.copy(val)
        print_into_plc("", clear=True)
        print_into_plc(val)
        print_into_plc("", True)

    def o_table_dclick(self, event):
        item = self.o_table.selection()[0]
        val = "o" + str(self.o_table.item(item)
                        ["values"][2]) + " " + self.o_table.item(item)["values"][0]
        # pyperclip.copy(val)
        print_into_plc("", clear=True)
        print_into_plc(val)
        print_into_plc("", True)

    def update_invalid_check(self, a):
        self.update_i_table()
        self.update_o_table()

    def inc_widget_id(self, event):
        if self.var_widget_id.get() == 16:
            self.var_widget_id.set(0)

    def dec_widget_id(self, event):
        if self.var_widget_id.get() == 1:
            self.var_widget_id.set(17)

    def change_widget_id(self):
        if not check_plc():
            return
        window = plc_widgets[TK_VARS["var_widget_id"].get() - 1]
        window.send_event(event.FocusIn(
            window=window,
            mode=X.NotifyNormal,
            detail=X.NONE))
        short_press(window=window, is_mouse=True)

    def update(self):
        check_plc()
        self.mainwindow.after(1000, self.update)


if __name__ == '__main__':
    app = UI()
    app.run()
