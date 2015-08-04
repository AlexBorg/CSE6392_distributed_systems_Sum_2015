#!/usr/bin/python3
import shelve
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog
from client_app import *

client = ClientApp()

class LoginFrame(Frame):
    """Show login screen"""
    def __init__(self, root):
        Frame.__init__(self, root)

        self.saved_settings = shelve.open("client_config.db", writeback=True)

        self.server   = StringVar(value=self.saved_settings.get("server", "localhost"))
        self.user     = StringVar(value=self.saved_settings.get("user", ""))
        self.password = StringVar(value=self.saved_settings.get("password", ""))

        Label(self, text="Server: ", anchor=W).grid(row=1, column=1, sticky="nsew")
        Label(self, text="Username: ", anchor=W).grid(row=2, column=1, sticky="nsew")
        Label(self, text="Password: ", anchor=W).grid(row=3, column=1, sticky="nsew")
        Entry(self, textvariable=self.server).grid(row=1, column=2, pady=5)
        Entry(self, textvariable=self.user).grid(row=2, column=2, pady=5)
        Entry(self, textvariable=self.password, show="*").grid(row=3, column=2, pady=5)

        box = Frame(self)
        Button(box, text="Register", command=self.register).pack(side=LEFT, expand=1, fill=BOTH)
        Button(box, text="Login", command=self.login).pack(side=LEFT, expand=1, fill=BOTH)
        box.grid(row=4, column=1, columnspan=2, sticky="nsew", pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

        client.register_message_listener(self)

    def login(self):
        client.connect_server(self.server.get())
        client.send_message(LoginData(self.user.get(), self.password.get()))

    def register(self):
        client.connect_server(self.server.get())
        client.send_message(RegisterRequest(self.user.get(), self.password.get()))

    def handle_LoginRegisterResponse(self, resp):
        if resp.success:
            self.saved_settings["server"] = self.server.get()
            self.saved_settings["user"] = self.user.get()
            self.saved_settings["password"] = self.password.get()
            self.saved_settings.sync()
        else:
            client.close_connection()
            messagebox.showerror("Login error", resp.error)

    def handle_ServerErrorMsg(self, resp):
        self.tkraise()
        messagebox.showerror("Server connection error", resp.error)


class ChatFrame(Frame):
    """Show room list and chat area"""
    def __init__(self, root):
        Frame.__init__(self, root)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        Label(self, text="Chat Rooms").grid(row=0, column=0, columnspan=2)

        self.groups = Listbox(self)
        self.groups.bind("<Double-Button-1>", self.join_group)
        self.groups.grid(row=1, column=0, sticky="nsew", columnspan=2, padx=2, pady=2)
        Button(self, text="Create", command=self.create_group).grid(row=2, column=0, sticky="nsew")
        Button(self, text="Join", command=self.join_group).grid(row=2, column=1, sticky="nsew")

        self.chat_text = dict()

        self.chat_tabs = Notebook(self)
        self.chat_tabs.grid(row=0, column=2, sticky="nsew", rowspan=2, columnspan=2)

        self.chat_say_text = StringVar()

        say_text_entry = Entry(self, textvariable=self.chat_say_text)
        say_text_entry.bind("<Return>", self.send_text)
        say_text_entry.grid(row=2, column=2, sticky="nsew")
        Button(self, text="Send", command=self.send_text).grid(row=2, column=3, sticky="nsew")

        client.register_message_listener(self)

    def add_group_tab(self, name):
        box = Frame(self.chat_tabs)
        t = Text(box, state=DISABLED)
        s = Scrollbar(box, command=t.yview)
        s.pack(side=RIGHT, fill=Y)
        t.config(yscrollcommand=s.set)
        t.pack(side=LEFT, expand=True, fill=BOTH)

        self.chat_text[name] = t
        self.chat_tabs.add(box, text=name, sticky="nsew")
        self.chat_tabs.select(self.get_group_tab(name))

    def get_group_tab(self, name):
        for id in self.chat_tabs.tabs():
            if self.chat_tabs.tab(id, "text") == name:
                return id
        return None

    def create_group(self):
        name = simpledialog.askstring("Create chat room", "Enter a name for the new chat room:")
        if name:
            self.add_group_tab(name)
            client.send_message(CreateGroupMsg(name))
            client.send_message(GroupSubscriptionData(name, True))

    def join_group(self, *args):
        group = self.groups.get(ACTIVE)
        tab = self.get_group_tab(group)
        if tab:
            self.chat_tabs.select(tab)
        else:
            client.send_message(GroupSubscriptionData(group, True))
            self.add_group_tab(group)

    def send_text(self, *args):
        if not self.chat_tabs.select() or not self.chat_say_text.get():
            return
        group = self.chat_tabs.tab(self.chat_tabs.select(), "text")
        client.send_message(MessageData(group, self.chat_say_text.get()))
        self.chat_say_text.set("")

    def handle_MessageData(self, msg):
        if msg.group in self.chat_text:
            box = self.chat_text[msg.group]
            box.config(state=NORMAL)
            box.insert(END, msg.message)
            box.see(END)
            box.config(state=DISABLED)

    def handle_LoginRegisterResponse(self, resp):
        if resp.success:
            self.tkraise()

    def handle_MsgGroupList(self, resp):
        self.groups.delete(0, END)
        for g in resp.groups:
            self.groups.insert(END, g)

    def handle_ChatErrorMsg(self, resp):
        messagebox.showerror("Error", resp.error)


if __name__ == "__main__":
    root = Tk()
    root.geometry("800x500")

    # Check for messages periodically and dispatch to registered GUI elements
    def task():
        client.check_messages()
        root.after(100, task)
    root.after(100, task)

    # Stack two frames on top of each other: Login and Chat area
    container = Frame(root)
    container.pack(side="top", fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    chat_frame = ChatFrame(container)
    chat_frame.grid(row=0, column=0, sticky="nsew")

    login_frame = LoginFrame(container)
    login_frame.grid(row=0, column=0, sticky="nsew")

    login_frame.tkraise()

    root.mainloop()