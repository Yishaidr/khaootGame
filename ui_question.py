import tkinter as tk
from server import TIMEOUT_QUESTION


class UiQuestion:
    """class that contain the ui of one question"""
    def submit(self):
        """ func that submit that handle answer of the player"""
        selected_option = self.var.get()
        if selected_option == self.correct_answer:
            self.result_label.config(text="Correct!", fg="green")
        else:
            self.result_label.config(text="Incorrect! the correct answer is " + self.correct_answer, fg="red")
        self.client.send_msg(selected_option)
        self.selected_answer_label.config(text=f"Your answer: {selected_option}")
        self.submit_button.config(state=tk.DISABLED)
        for option in self.option_buttons:
            option.config(state=tk.DISABLED)
        self.answer_question = True

    def update_timer(self):
        """ func that handle the timeout for a question"""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_label.config(text=f"Time remaining: {self.time_remaining} seconds")
            self.root.after(1000, self.update_timer)  # Call update_timer again after 1 second
        else:
            if not self.answer_question:  # if he did not answer the question after the Timeout
                self.client.send_msg("no answer")
            self.root.destroy()

    def __init__(self, client, question, answers, correct_answer):
        # Create main window
        self.client = client
        self.root = tk.Tk()
        self.root.title(self.client.name)
        self.root.configure(bg="purple")
        self.answer_question = False
        window_width = 700
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (window_width / 2))
        y_coordinate = int((screen_height / 2) - (window_height / 2))
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Define the question and answers
        self.correct_answer = correct_answer

        # Create frame for question and answers
        frame = tk.Frame(self.root, bg="purple")
        frame.pack(expand=True)

        # Create label for question
        question_label = tk.Label(frame, text=question, font=("Arial", 20), bg="purple", fg="white")
        question_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Create radio buttons for answer options
        var = tk.StringVar()
        self.option_buttons = []
        for i, answer in enumerate(answers):
            option = tk.Radiobutton(frame, text=answer, variable=var, value=answer, bg="purple", fg="white", font=("Arial", 20))
            option.grid(row=i+1, column=0, padx=10, pady=5, sticky="w")
            self.option_buttons.append(option)
        self.var = var

        # Create button to submit the answer
        submit_button = tk.Button(frame, text="Submit", command=self.submit, bg="purple", fg="white", font=("Arial", 12))
        submit_button.grid(row=len(answers)+1, column=0, columnspan=2, pady=10)
        self.submit_button = submit_button

        # Create label to display result
        result_label = tk.Label(self.root, text="", font=("Arial", 20), bg="purple", fg="white")
        result_label.pack(pady=5)
        self.result_label = result_label

        # Create label to display selected answer
        selected_answer_label = tk.Label(self.root, text="", font=("Arial", 20), bg="purple", fg="white")
        selected_answer_label.pack()
        self.selected_answer_label = selected_answer_label

        # Create label to display timer
        self.time_remaining = TIMEOUT_QUESTION
        timer_label = tk.Label(self.root, text=f"Time remaining: {self.time_remaining} seconds", font=("Arial", 20), bg="purple", fg="white")
        timer_label.pack()
        self.timer_label = timer_label

        # Start the timer
        self.update_timer()

        # Run the Tkinter event loop
        self.root.mainloop()
