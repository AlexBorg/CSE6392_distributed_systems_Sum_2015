

from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

from client_app import *

#tab code borrowed from:
# http://code.activestate.com/recipes/577261-python-tkinter-tabs/

BASE = RAISED
SELECTED = FLAT

# a base tab class
class Tab(Frame):
    def __init__(self, master, name):
        Frame.__init__(self, master)
        self.tab_name = name


# the bulk of the logic is in the actual tab bar
class TabBar(Frame):
    def __init__(self, master=None, init_name=None):
        Frame.__init__(self, master)
        self.tabs = {}
        self.buttons = {}
        self.current_tab = None
        self.init_name = init_name

    def show(self):
        self.pack(side=TOP, expand=YES, fill=X)
        self.switch_tab(self.init_name or self.tabs.keys()[-1])# switch the tab to the first tab

    def add(self, tab):
        tab.pack_forget()									# hide the tab on init

        self.tabs[tab.tab_name] = tab						# add it to the list of tabs
        b = Button(self, text=tab.tab_name, relief=BASE,    # basic button stuff
            command=(lambda name=tab.tab_name: self.switch_tab(name)))  # set the command to switch tabs
        b.pack(side=LEFT)												# pack the buttont to the left mose of self
        self.buttons[tab.tab_name] = b											# add it to the list of buttons

    def delete(self, tabname):

        if tabname == self.current_tab:
            self.current_tab = None
            self.tabs[tabname].pack_forget()
            del self.tabs[tabname]
            self.switch_tab(self.tabs.keys()[0])

        else: del self.tabs[tabname]

        self.buttons[tabname].pack_forget()
        del self.buttons[tabname]

    def switch_tab(self, name):
        if self.current_tab:
            self.buttons[self.current_tab].config(relief=BASE)
            self.tabs[self.current_tab].pack_forget()			# hide the current tab
        self.tabs[name].pack(side=BOTTOM)							# add the new tab to the display
        self.current_tab = name									# set the current tab to itself

        self.buttons[name].config(relief=SELECTED)					# set it to the selected style

# end tab section


class ClientGUI:
    def __init__(self, ob_root_window):
        self.ob_root_window = ob_root_window
        self.menu = ClMenu(self)

        self.client = ClientApp(self.message_callback)

        self.tab_bar = TabBar(self.ob_root_window, 'tab1')
        self.tab1 = Tab(self.ob_root_window, "tab1")
        self.tab2 = Tab(self.ob_root_window, "tab2")
        self.tab3 = Tab(self.ob_root_window, "tab3")

        self.tab_bar.add(self.tab1)
        self.tab_bar.add(self.tab2)
        self.tab_bar.add(self.tab3)

        self.tab_bar.show()

    def message_callback(self, group, message):
        print("callback called with " + message)

class ClMenu:
    def __init__(self, master):

        self.master = master
        self.menu = Menu(master.ob_root_window)
        master.ob_root_window.config(menu=self.menu)
        self.file_menu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.menu_callback)
        self.file_menu.add_command(label="Open...", command=self.menu_callback)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=close_window_callback)

        self.help_menu = Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About...", command=self.menu_help_callback)

    def menu_callback(self):
        print("called the menu callback!")

    def menu_help_callback(self):
        print("called the help menu callback!")


def close_window_callback(root):
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()


def gui_main():
    base_window = Tk()
    base_window.protocol("WM_DELETE_WINDOW", lambda root_window=base_window: close_window_callback(root_window))
    ClientGUI(base_window)
    base_window.mainloop()


if __name__ == "__main__":
    gui_main()