import tkinter as tk
from tkinter import ttk


class UiCrateGame:

    def update_player_list(self):
        # Sample player list (replace with your player data)
        self.client.send_msg("give me list of player")
        players = self.client.get_msg().split(",")  # get a list of player from the server
        # Clear previous player labels
        for widget in players_frame.winfo_children():
            widget.destroy()

        # Create new player labels
        for player in players:
            player_label = tk.Label(players_frame, text=player, font=("Arial", 12), bg="purple", fg="white")
            player_label.pack()

        # Schedule the next update after 1 second
        players_frame.after(1000, self.update_player_list)

    def start_game(self):
        """ it pushed when we want to start a game"""
        print("Game started...")
        self.client.send_msg("start")
        self.client.get_msg()
        self.client.send_msg("okay")
        new_window.destroy()

    def submit(self):
        """ handle choosing category and num of questions"""
        selected_category = category_var.get()
        selected_questions = questions_var.get()

        self.client.send_msg(selected_category + "," + str(selected_questions))  # send the category and the number
        # of questions
        self.client.get_msg()

        self.root.destroy()  # Close the current window

        # Create a new window for displaying category and player list
        global new_window
        new_window = tk.Tk()
        new_window.title(self.pin_game)
        new_window.configure(bg="purple")

        # Set window size
        window_width = 700
        window_height = 700
        screen_width = new_window.winfo_screenwidth()
        screen_height = new_window.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        new_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        global players_frame
        players_frame = tk.Frame(new_window, bg="purple")
        players_frame.pack(expand=True, padx=20, pady=20)

        question_label = tk.Label(players_frame, text="players list", font=("Arial", 20), bg="purple", fg="white")
        question_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Update player list initially
        self.update_player_list()

        # Start game button
        start_game_button = tk.Button(new_window, text="Start Game", command=self.start_game, bg="purple", fg="white",
                                      font=("Arial", 12))
        start_game_button.pack(pady=20)

        # Run the Tkinter event loop for the new window
        new_window.mainloop()

    def __init__(self, client, pin_game):
        self.pin_game = pin_game
        self.client = client
        # Create main window
        self.root = tk.Tk()
        self.root.title("Game Pin : " + self.pin_game)
        self.root.configure(bg="purple")

        # Set window size
        window_width = 700
        window_height = 700
        self.root.geometry(f"{window_width}x{window_height}")

        # Create frame
        frame = tk.Frame(self.root, bg="purple")
        frame.pack(expand=True, padx=20, pady=20)

        # Create label for title
        title_label = tk.Label(frame, text="Game Pin : " + self.pin_game, font=("Arial", 20), bg="purple", fg="white")
        title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Category selection
        category_label = tk.Label(frame, text="Choose category:", font=("Arial", 12), bg="purple", fg="white")
        category_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        categories = self.client.get_msg().split(",")  # get a list of categories from the server
        global category_var
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(frame, textvariable=category_var, values=categories)
        category_dropdown.grid(row=1, column=1, padx=10, pady=10)
        category_dropdown.current(0)

        # Number of questions selection
        questions_label = tk.Label(frame, text="Choose number of questions:", font=("Arial", 12), bg="purple", fg="white")
        questions_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        global questions_var
        questions_var = tk.IntVar()
        questions_spinbox = tk.Spinbox(frame, from_=3, to=5, textvariable=questions_var, bg="white", font=("Arial", 12))
        questions_spinbox.grid(row=2, column=1, padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(frame, text="Submit", command=self.submit, bg="purple", fg="white", font=("Arial", 12))
        submit_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Run the Tkinter event loop
        self.root.mainloop()


