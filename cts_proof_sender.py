import queue
import sqlite3
import threading
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from proof_of_transport.crawlers import download_last_proof_of_transport
from proof_of_transport.exceptions import LoginException
from proof_of_transport.mail import MailClient

con = sqlite3.connect('userdata.db')
send_errors_queue = queue.Queue()


def handle_send_thread(login: str, password: str, mail_client: MailClient, to_email: str):
    try:
        filepath = download_last_proof_of_transport(login, password)
        mail_client.send_file_to(filepath, to_email)
    except Exception as e:
        send_errors_queue.put(e)
        return
    send_errors_queue.put(None)


class App(Tk):
    def __init__(self, canvas_width, canvas_height):
        super().__init__()
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS app_settings(
                                id INTEGER PRIMARY KEY,
                                login TEXT,
                                password TEXT,
                                from_email TEXT,
                                to_email TEXT
                            )
                        ''')
        con.commit()
        self.resizable(False, False)
        self.title('CTS-proof-sender')
        self.mail_client = None
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
        entry_width = 17

        self.entries = {}
        # Send email from
        row = Frame(self)
        lab = Label(row, width=entry_width, text="Send from: ", anchor='w')
        ent = Entry(row)
        row.grid(row=0, column=0, padx=10, pady=5)
        # row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.entries["SendFrom"] = ent

        # Send email to
        row = Frame(self)
        lab = Label(row, width=entry_width, text="Send to: ", anchor='w')
        ent = Entry(row)
        row.grid(row=1, column=0, padx=10, pady=5)
        # row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.entries['SendTo'] = ent

        # Login
        row = Frame(self)
        lab = Label(row, width=entry_width, text="CTS Login: ", anchor='w')
        ent = Entry(row)
        row.grid(row=2, column=0, padx=10, pady=5)
        # row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.entries['Login'] = ent

        # Password
        row = Frame(self)
        lab = Label(row, width=entry_width, text="CTS Password: ", anchor='w')
        ent = Entry(row, show='*')
        row.grid(row=3, column=0)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.entries['Password'] = ent

        # Initialize entries
        cur = con.cursor()
        cur.execute("SELECT * FROM app_settings WHERE id=?", (1,))
        app_settings = cur.fetchone()
        if app_settings is not None:
            self.entries['Login'].insert(END, app_settings[1])
            self.entries['Password'].insert(END, app_settings[2])
            self.entries['SendFrom'].insert(END, app_settings[3])
            self.mail_client = MailClient(app_settings[3])
            self.entries['SendTo'].insert(END, app_settings[4])

        # Progress frame
        self.progress_frame = Frame(self)

        # configure the grid to place the progress bar is at the center
        self.progress_frame.columnconfigure(0, weight=1)
        self.progress_frame.rowconfigure(0, weight=1)

        # progressbar
        self.pb = Progressbar(self.progress_frame, orient=HORIZONTAL, mode='indeterminate')
        self.pb.grid(row=4, column=0, sticky=EW, padx=10, pady=10)

        # place the progress frame
        self.progress_frame.grid(sticky=NSEW)

        # Buttons
        self.send_button = Button(self, text='Send', command=self.handle_send)
        self.send_button.grid(row=5, column=0, sticky=SW, padx=10)
        quit_button = Button(self, text='Quit', command=self.quit)
        quit_button.grid(row=5, column=0, sticky=SE, padx=10)

        self.pb.grid_remove()

    def start_sending(self):
        self.pb.grid()
        self.pb.start(20)
        self.send_button.after(100, self.after_send)

    def stop_sending(self):
        self.pb.stop()
        self.pb.grid_remove()

    def handle_send(self):
        from_email = self.entries['SendFrom'].get()
        if self.mail_client is None or self.mail_client.from_email != from_email:
            self.mail_client = MailClient(from_email)
        login = self.entries['Login'].get()
        password = self.entries['Password'].get()
        to_email = self.entries['SendTo'].get()
        cur = con.cursor()
        cur.execute("INSERT INTO app_settings VALUES (:id, :login, :password, :from_email, :to_email) ON "
                    "CONFLICT(id) DO UPDATE SET "
                    "login=excluded.login, password=excluded.password, from_email=excluded.from_email, "
                    "to_email=excluded.to_email", {
                        'id': 1,
                        'login': login,
                        'password': password,
                        'from_email': from_email,
                        'to_email': to_email,
                    })

        con.commit()
        self.start_sending()
        args = [login, password, self.mail_client, to_email]
        threading.Thread(target=handle_send_thread, args=args).start()

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
    app = App(380, 215)
    app.mainloop()
