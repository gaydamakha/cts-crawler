import queue
import sqlite3
import threading
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from proof_of_transport.functions import proof_of_transport
from proof_of_transport.exceptions import LoginException

LOGIN_RECORD_ID = 1

con = sqlite3.connect('userdata.db')
send_errors_queue = queue.Queue()


def handle_send_thread(login, password):
    try:
        proof_of_transport(login, password)
    except Exception as e:
        send_errors_queue.put(e)
        return
    send_errors_queue.put(None)


class App(Tk):
    def __init__(self, canvas_width, canvas_height):
        super().__init__()
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS record(
                                id INTEGER PRIMARY KEY,
                                login TEXT,
                                password text
                            )
                        ''')
        con.commit()
        self.resizable(False, False)
        self.title('CTS-proof-sender')
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (canvas_width / 2)
        y = (hs / 2) - (canvas_height / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (canvas_width, canvas_height, x, y))

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        cur = con.cursor()
        cur.execute("SELECT * FROM record WHERE id=?", (LOGIN_RECORD_ID,))
        login_info = cur.fetchone()

        self.entries = {}
        # Login
        row = Frame(self)
        lab = Label(row, width=10, text="Login: ", anchor='w')
        ent = Entry(row)
        if login_info is not None:
            ent.insert(END, login_info[1])

        row.grid(row=0, column=0, padx=10, pady=5)
        # row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.entries["Login"] = ent

        # Password
        row = Frame(self)
        lab = Label(row, width=10, text="Password: ", anchor='w')
        ent = Entry(row, show='*')
        if login_info is not None:
            ent.insert(END, login_info[2])
        row.grid(row=1, column=0)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.entries["Password"] = ent

        # Progress frame
        self.progress_frame = Frame(self)

        # configure the grid to place the progress bar is at the center
        self.progress_frame.columnconfigure(0, weight=1)
        self.progress_frame.rowconfigure(0, weight=1)

        # progressbar
        self.pb = Progressbar(self.progress_frame, orient=HORIZONTAL, mode='indeterminate')
        self.pb.grid(row=2, column=0, sticky=EW, padx=10, pady=10)

        # place the progress frame
        self.progress_frame.grid(sticky=NSEW)

        # Buttons
        self.send_button = Button(self, text='Send', command=self.handle_send)
        self.send_button.grid(row=3, column=0, sticky=SW, padx=10)
        b2 = Button(self, text='Quit', command=self.quit)
        b2.grid(row=3, column=0, sticky=SE, padx=10)

        self.pb.grid_remove()

    def start_sending(self):
        self.pb.grid()
        self.pb.start(20)
        self.send_button.after(100, self.after_send)

    def stop_sending(self):
        self.pb.stop()
        self.pb.grid_remove()

    def handle_send(self):
        login = self.entries['Login'].get()
        password = self.entries['Password'].get()
        cur = con.cursor()
        cur.execute("INSERT INTO record VALUES (:id, :login, :password) ON CONFLICT(id) DO UPDATE SET "
                    "login=excluded.login, password=excluded.password", {
                        'id': LOGIN_RECORD_ID,
                        'login': login,
                        'password': password,
                    })
        con.commit()
        self.start_sending()
        threading.Thread(target=handle_send_thread, args=[login, password]).start()

    def after_send(self):
        try:
            message = send_errors_queue.get(block=False)
        except queue.Empty:
            self.send_button.after(100, self.after_send)
            return
        if message is not None:
            if isinstance(message, LoginException):
                messagebox.showerror('Login error', str(message))
            elif isinstance(message, Exception):
                messagebox.showerror('Unknown error', str(message))
        self.stop_sending()


if __name__ == '__main__':
    app = App(300, 150)
    app.mainloop()
