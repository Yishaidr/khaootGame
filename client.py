import tkinter as tk
import socket
from server import OKAY, NO, YES, START_GAME, GAME_OVER
from ui_question import UiQuestion
from ui_crate_game import UiCrateGame
HOST = socket.gethostbyname(socket.gethostname())
PORT = 65432  # The port used by the


class Client:
    """ this is a class that represent the client(player)"""

    def send_msg(self, msg):
        self.connection.sendall(msg.encode())

    def get_msg(self):
        return self.connection.recv(1024).decode()

    def on_submit_name(self):
        """ func that handle the choosing of the name"""
        self.name = name_entry.get()
        if self.name:
            self.send_msg(self.name)
            welcome_label.config(text=f"Welcome, {self.name}!")
            entry_frame.pack_forget()  # Hide entry frame
            main_frame.pack()  # Show main frame with buttons
        else:
            # Notify the user to enter a name
            error_label.config(text="Please enter your name.")

    def answer_question(self):
        """ handle the player answering the question"""
        self.send_msg(OKAY)
        question = self.get_msg()  # get the question from the server
        answers = []
        for i in range(4):  # get the possible answers for the question from the server
            self.send_msg(OKAY)
            answers.append(self.get_msg())
        self.send_msg(OKAY)
        correct_answer = self.get_msg()
        UiQuestion(self, question, answers, correct_answer)  # crate the question in the gui
        self.get_msg()  # status of answer
        self.handle_after_the_player_answer()

    def handle_after_the_player_answer(self):
        finish = NO
        while finish != YES:  # ask the server of all the player finish
            self.send_msg("finish?")
            finish = self.get_msg()
        scoreboard = self.get_msg()
        self.display_scoreboard(scoreboard.split("\n"), "THE SCORE", 3500)  # display the scoreboard
        self.send_msg(OKAY)

    def enter_game(self):
        """func that handle player who want to enter a game until it start"""
        self.send_msg("enter")
        root.destroy()
        answer = self.get_msg()
        print(answer)
        pin = input()
        self.send_msg(pin)
        answer = self.get_msg()
        print(answer)
        # wait until the player enter exiting game pin
        while answer != "you enter the game wait for the game to start":
            pin = input()
            self.send_msg(pin)
            answer = self.get_msg()
            print(answer)
        start = ""
        while start != START_GAME:  # wait when the leader decide to start the game
            self.send_msg("start?")
            start = self.get_msg()
        self.send_msg(OKAY)

    def crate_game(self):
        """func that the handle the creation of new quizz game until he starts"""
        self.send_msg("crate")
        root.destroy()
        game_pin = self.get_msg()
        self.send_msg(OKAY)
        UiCrateGame(self, game_pin)

    def play_game(self):
        """ the func that handle a single player from the client side"""
        self.crate_ui()
        while True:
            msg = self.get_msg()
            if msg == GAME_OVER:
                self.send_msg(OKAY)
                scoreboard = self.get_msg()
                self.display_scoreboard(scoreboard.split("\n"), GAME_OVER, 10000)
                break
            else:
                self.answer_question()

    def display_scoreboard(self, scoreboard, label_text, time_to_live):
        """ func that display the current score bord and die after time_to_live pass"""
        # Create main window
        root = tk.Tk()
        root.title("scoreboard - " + self.name)
        root.configure(bg="purple")

        # Set window size
        window_width = 700
        window_height = 700

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate position to center window
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2

        # Set window position
        root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Create label for the label to show
        game_over_label = tk.Label(root, text=label_text, font=("Arial", 25), bg="purple", fg="white")
        game_over_label.pack(pady=20)

        # Sort scoreboard by score from highest to lowest
        sorted_scoreboard = sorted(scoreboard, key=lambda x: float(x.split(":")[1]), reverse=True)

        # Display scoreboard
        for i in range(len(sorted_scoreboard)):
            name, score = sorted_scoreboard[i].split(":")
            if name == self.name:  # the player itself will be in red
                score_label = tk.Label(root, text=f"{i + 1}. {name}: {score}", font=("Arial", 20), bg="purple",
                                       fg="green")
            else:
                score_label = tk.Label(root, text=f"{i + 1}. {name}: {score}", font=("Arial", 20), bg="purple",
                                       fg="white")
            score_label.pack()

        # Close the window after 10 seconds
        root.after(time_to_live, root.destroy)

        # Run the Tkinter event loop
        root.mainloop()

    def crate_ui(self):
        global entry_frame, name_entry, error_label, main_frame, welcome_label, root
        # Create main window
        root = tk.Tk()
        root.title("Chen Khoot game")
        root.configure(bg="purple")
        # Calculate the middle of the window
        window_width = 700
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (window_width / 2))
        y_coordinate = int((screen_height / 2) - (window_height / 2))
        # Set window size and position
        root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        # Create entry frame for name input
        entry_frame = tk.Frame(root, bg="purple")
        entry_frame.pack(expand=True)
        # Create label and entry for name input
        name_label = tk.Label(entry_frame, text="Enter your name:", font=("Arial", 14), bg="purple", fg="white")
        name_label.pack(pady=20)
        name_entry = tk.Entry(entry_frame, font=("Arial", 12))
        name_entry.pack(padx=20, pady=(0, 20))
        submit_button = tk.Button(entry_frame, text="Submit", command=self.on_submit_name, bg="purple", fg="white",
                                  font=("Arial", 12))
        submit_button.pack(pady=(0, 20))
        error_label = tk.Label(entry_frame, text="", font=("Arial", 12), bg="purple", fg="red")
        error_label.pack()
        # Create main frame to hold buttons
        main_frame = tk.Frame(root, bg="purple")
        # Create label for the welcome message
        welcome_label = tk.Label(main_frame, text="", font=("Arial", 20), bg="purple", fg="white")
        welcome_label.pack(pady=(50, 20))
        # Create buttons
        button1 = tk.Button(main_frame, text="enter game", command=self.enter_game, bg="purple", fg="white", font=("Arial", 12),
                            padx=20, pady=10)
        button1.pack(side=tk.LEFT, padx=10)
        button2 = tk.Button(main_frame, text="crate game", command=self.crate_game, bg="purple", fg="white", font=("Arial", 12),
                            padx=20, pady=10)
        button2.pack(side=tk.LEFT, padx=10)
        # Run the Tkinter event loop
        root.mainloop()

    def __init__(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            self.connection = s
            self.name = ""
            self.play_game()

Client()





