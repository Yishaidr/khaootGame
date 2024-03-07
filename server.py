import random
from datetime import datetime
import socket
import threading
import time
from questions import questions

CORRECT_ANSWERS = "correct_answers"

OKAY = "okay"

NO = "no"

ENTER_GAME_PIN_ = "enter game pin?"

START_GAME = "start game"

THE_GAME_PIN_ = "the game pin: "

FOR_THE_GAME_TO_START = "you enter the game wait for the game to start"

GAME_NOT_REDY = "game not redy"

THE_GAME_PIN_IS_ = "the game pin is: "

YES = "yes"

GAME_THE_PLAYERS_ARE_ = "do you want to start the game?\n the players are: "

NEW_QUESTION = "new question"

GAME_OVER = "GAME OVER"

ANSWER = "answer"

SCORE = "score"

START = "start"

PLAYERS = "players"

ANSWERS = "answers"

OPTIONS = "options"

QUESTIONS = "questions"

TIMEOUT_QUESTION = 10

CORRECT_SCORE = 100

CUR_GAME = {}

HOST = socket.gethostbyname(socket.gethostname())
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


class Server:

    @staticmethod
    def get_questions_and_options_and_answers(selected_category, num_of_questions):
        """
        get a random set of questions and answers
        :param selected_category: the category the user want to use
        :param num_of_questions: num_of_questions
        :return:  random set of questions and options and answers of the size of num_of_questions
        """
        place_of_first_question = random.randint(0, len(questions[selected_category][QUESTIONS]) - num_of_questions)
        return questions[selected_category][QUESTIONS][place_of_first_question: place_of_first_question +
                                                                                num_of_questions], \
               questions[selected_category][OPTIONS][
               place_of_first_question: place_of_first_question + num_of_questions], \
               questions[selected_category][CORRECT_ANSWERS][
               place_of_first_question: place_of_first_question + num_of_questions]

    def do_one_question(self, correct_answer, options_guesses, question):
        """
        handle a one question guesses
        :param correct_answer: the correct_answer for this question
        :param options_guesses: the possible for the question
        :param question: the question the user gets ask
        """
        self.send_question_and_answer(correct_answer, options_guesses, question)
        points = self.handle_guess(correct_answer)
        self.score += points  # change the player score base of the current question
        CUR_GAME[self.game_pin][PLAYERS][self.name][SCORE] = self.score
        CUR_GAME[self.game_pin][PLAYERS][self.name][ANSWER] = True  # update that this player answer the question
        self.wait_until_all_player_answer()  # or timeout
        time.sleep(2)  # we want to be sure that every budy release that all the player finish
        for entry in CUR_GAME[self.game_pin][PLAYERS].values():
            entry[ANSWER] = False  # we change that every player did not answer
        time.sleep(2)  # we want to be sure that every budy release that all the player finish
        self.send_score_bord()
        self.get_msg()

    def wait_until_all_player_answer(self):
        """ wait until all player answer or timeout by checking the global dict"""
        all_player_in_game_answer = False
        while not all_player_in_game_answer:  # check if all the player answer
            self.get_msg()
            players_dict = CUR_GAME[self.game_pin][PLAYERS]
            all_player_in_game_answer = all(entry[ANSWER] for entry in players_dict.values())
            if not all_player_in_game_answer:
                self.send_msg(NO)  # say not all player answer
            else:
                self.send_msg(YES)

    def send_question_and_answer(self, correct_answer, options_guesses, question):
        self.get_msg()
        self.send_msg(question)
        for option in options_guesses:
            self.get_msg()
            self.send_msg(option)
        self.get_msg()
        self.send_msg(correct_answer)

    def handle_guess(self, correct_answer):
        """
        handle guess for one question and calculate the points
        :param: correct_answer:
        :return: the player point from this question
        """
        start_time = datetime.now()
        points = 0
        user_input = self.get_msg()
        end_time = datetime.now()
        time_passed = end_time - start_time
        time_passed_seconds = time_passed.total_seconds()  # Convert the time difference to seconds
        if user_input == correct_answer:
            self.send_msg("wow you are correct")
            points = max(CORRECT_SCORE - time_passed_seconds * (CORRECT_SCORE / TIMEOUT_QUESTION), 0)
            # calculate the points based on the time it take to answer
        else:
            self.send_msg("you are worng the correct answer is: " + correct_answer)
        return points

    def send_score_bord(self):
        """func that send score bord of the quizz game"""
        dict_of_player = CUR_GAME[self.game_pin][PLAYERS]
        # Sort the dictionary items based on the scores (from highest to lowest)
        sorted_data = sorted(dict_of_player.items(), key=lambda x: x[1][SCORE], reverse=True)

        # Get string of the name and score from the highest score to lowest
        result = "\n".join([f"{name}:{score[SCORE]}" for name, score in sorted_data])
        self.send_msg(result)

    def send_msg(self, msg):
        self.connection.sendall(msg.encode())

    def get_msg(self):
        msg = self.connection.recv(1024).decode()
        return msg

    def enter_or_crate_game(self):
        answer = self.get_msg()
        if answer == "crate":
            self.crate_game()
        else:
            self.enter_game()
        self.send_msg(START_GAME)

    def enter_game(self):
        """func that handle player who want to enter a game and wait until the game start"""
        self.send_msg(ENTER_GAME_PIN_)
        answer = self.get_msg()
        while answer not in CUR_GAME or CUR_GAME[answer][START]:  # get game pin from player
            self.send_msg(THE_GAME_PIN_ + answer + " do not in db try different one or the game already started")
            answer = self.get_msg()
        self.game_pin = answer
        self.send_msg(FOR_THE_GAME_TO_START)
        CUR_GAME[self.game_pin][PLAYERS][self.name] = {SCORE: self.score, ANSWER: False}
        while True:  # wait until the game start that is start when the player that crate the game change the
            # start to true
            self.get_msg()
            if CUR_GAME[self.game_pin][START]:
                return
            else:
                self.send_msg(GAME_NOT_REDY)

    def crate_game(self):
        """ func that crate a quizz game and wait until the player want to start"""
        self.game_pin = str(random.randint(0, 1000))  # generate a game pin
        self.send_msg(self.game_pin)
        self.get_msg()
        self.send_msg(",".join(questions.keys()))
        msg = self.get_msg().split(",")
        selected_category = msg[0]
        num_of_questions = msg[1]
        self.send_msg(OKAY)
        questions_game, options_game, answers_game = self.get_questions_and_options_and_answers(selected_category,
                                                                                                int(num_of_questions))
        CUR_GAME[self.game_pin] = {QUESTIONS: questions_game, OPTIONS: options_game, ANSWERS: answers_game, PLAYERS:
            {self.name: {SCORE: self.score, ANSWER: False}}, START: False}  # add game to dict that indict the games
        answer = self.get_msg()
        while answer != START:  # wait until the player want to start the game
            players = ",".join(CUR_GAME[self.game_pin][PLAYERS].keys())
            self.send_msg(players)
            answer = self.get_msg()
        CUR_GAME[self.game_pin].update({START: True})  # start the game

    def play_game(self):
        """ the func that handle a single player """
        self.enter_or_crate_game()
        self.get_msg()
        for question_num in range(len(CUR_GAME[self.game_pin][QUESTIONS])):
            self.send_msg(NEW_QUESTION)
            self.do_one_question(CUR_GAME[self.game_pin][ANSWERS][question_num], CUR_GAME[self.game_pin][OPTIONS]
            [question_num], CUR_GAME[self.game_pin][QUESTIONS][question_num])
        self.send_msg(GAME_OVER)
        self.get_msg()
        self.send_score_bord()

    def __init__(self, conn, addr):
        self.connection = conn
        self.name = self.get_msg()
        self.score = 0
        self.game_pin = ""
        with conn:
            print(f"Connected by {addr}")
            self.play_game()


def crate_server(connection, adr):
    Server(connection, adr)


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        CUR_GAME = {}  # hold all the information of all the games
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=crate_server, args=(conn, addr))
            thread.start()
