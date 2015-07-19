

from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

from client_app import *

# tab code borrowed from:
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
    def __init__(self, root_window):
        self.root_window = root_window
        self.menu = ClMenu(self)

        self.client = ClientApp()

        self.tab_bar = TabBar(self.root_window, 'servers')
        self.select_servers_tab = Tab(self.root_window, "servers")
        self.select_servers_frame = SelectServerFrame(self, self.select_servers_tab)

        self.tab_bar.add(self.select_servers_tab)

        self.group_tabs = set()
        self.group_frames = set()

        self.server_tabs = set()
        self.server_frames = set()
        # self.tab2 = Tab(self.root_window, "tab2")
        # self.tab_bar.add(self.tab2)

        self.tab_bar.show()
        self.check_messages()

    def check_messages(self):
        message = self.client.check_messages()
        if message is None:
            self.root_window.after(200, self.check_messages)
        else:
            for group_frame in self.group_frames:
                group_frame.post_message(message)
            self.root_window.after(0, self.check_messages)

    def connect_server(self, server_name):
        result_err, message = self.client.connect_server(server_name, "name", "password")
        if result_err:
            print(message)
            return

        server_tab = Tab(self.root_window, server_name)
        server_frame = ServerFrame(self, server_tab, server_name)
        self.tab_bar.add(server_tab)
        self.tab_bar.switch_tab(server_name)

        self.server_tabs.add(server_tab)
        self.server_frames.add(server_frame)

    def join_group(self, group_name):
        result_err, message = self.client.join_group(group_name)
        if result_err:
            print(message)
            return

        group_tab = Tab(self.root_window, group_name)
        group_frame = GroupFrame(self, group_tab, group_name)
        self.tab_bar.add(group_tab)
        self.tab_bar.switch_tab(group_name)

        self.server_tabs.add(group_tab)
        self.server_frames.add(group_frame)


class ClMenu:
    def __init__(self, master):

        self.master = master
        self.menu = Menu(master.root_window)
        master.root_window.config(menu=self.menu)
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


class SelectServerFrame:
    def __init__(self, master, owning_tab):
        self.master = master
        self.owning_tab = owning_tab

        self.listbox = Listbox(owning_tab)
        self.listbox.pack(side=TOP)
        button = Button(owning_tab, text="Connect Server", command=self.connect_server)
        button.pack(side=TOP)

        button = Button(owning_tab, text="Update List", command=self.update_list)
        button.pack(side=TOP)

    def connect_server(self):
        selection = self.listbox.curselection()
        server_name = self.listbox.get(selection[0])
        self.master.connect_server(server_name)

    def update_list(self):
        servers = self.master.client.get_server_names()
        self.listbox.delete(0, END)
        for server in servers:
            self.listbox.insert(END, server.name)
        self.listbox.activate(1)


class ServerFrame:
    def __init__(self, master, owning_tab, server_name):
        self.master = master
        self.owning_tab = owning_tab
        self.server_name = server_name

        self.listbox = Listbox(owning_tab)
        self.listbox.pack(side=TOP)
        button = Button(owning_tab, text="Join Group", command=self.join_group)
        button.pack(side=TOP)

        button = Button(owning_tab, text="Update List", command=self.update_list)
        button.pack(side=TOP)

        self.entry = Entry(owning_tab, width=50)
        self.entry.insert(0, '')
        self.entry.pack(side=TOP)
        button = Button(owning_tab, text="Create Group", command=self.create_group)
        button.pack(side=LEFT)

    def join_group(self):
        selection = self.listbox.curselection()
        server_name = self.listbox.get(selection)
        self.master.connect_server(server_name)

    def update_list(self):
        servers = self.master.client.get_group_names()
        self.listbox.delete(0, END)
        for server in servers:
            self.listbox.insert(END, server.name)
        self.listbox.activate(1)

    def create_group(self):
        self.master.join_group(self.entry.get())


class GroupFrame:
    def __init__(self, master, owning_tab, group_name):
        self.master = master
        self.owning_tab = owning_tab
        self.group_name = group_name

        self.display = Text(owning_tab, height=10, width=40)
        self.display.pack(side=TOP)
        self.entry = Entry(owning_tab, width=50)
        self.entry.insert(0, '')
        self.entry.pack(side=TOP)
        self.button = Button(owning_tab, text="Send", command=self.send_message)
        self.button.pack(side=TOP)

    def send_message(self):
        self.master.client.send_message(self.group_name, "send message")


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