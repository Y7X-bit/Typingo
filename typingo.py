import customtkinter as ctk
import time
import random
import json
from pathlib import Path
from difflib import SequenceMatcher
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TypingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Test • Y7X")
        self.root.geometry("580x420")
        self.root.resizable(False, False)

        self.sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "Python is a high-level, interpreted programming language.",
            "Practice makes perfect when learning to type quickly.",
            "Logic and patience are key in programming.",
            "How vexingly quick daft zebras jump!"
        ]

        self.best_scores = {"wpm": 0, "accuracy": 0}
        self.score_file = "scores.json"
        self.load_scores()

        self.practice_mode_on = False
        self.practice_start_time = 0
        self.practice_sentence_count = 0
        self.practice_chars = 0
        self.practice_correct = 0
        self.practice_total = 0

        self.start_time = None
        self.timer_running = False

        self.setup_ui()

    def load_scores(self):
        if Path(self.score_file).exists():
            with open(self.score_file, "r") as f:
                self.best_scores = json.load(f)

    def save_scores(self):
        with open(self.score_file, "w") as f:
            json.dump(self.best_scores, f)

    def get_random_sentence(self):
        return random.choice(self.sentences)

    def calculate_wpm(self, typed_chars, time_taken):
        words = typed_chars / 5
        minutes = time_taken / 60
        return round(words / minutes, 2) if minutes > 0 else 0

    def calculate_accuracy(self, original, typed):
        matcher = SequenceMatcher(None, original, typed)
        return round(matcher.ratio() * 100, 2)

    def styled_button(self, master, text, command):
        return ctk.CTkButton(master, text=text, width=180, height=38, corner_radius=12,
                             fg_color="#222831", hover_color="#00adb5",
                             border_width=2, border_color="#00fff5", command=command)

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.frame.pack(expand=True, fill="both", padx=30, pady=20)
        self.frame.grid_columnconfigure((0, 1), weight=1)

        self.title_label = ctk.CTkLabel(self.frame, text="Typing Test", font=("Segoe UI", 24, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(8, 15))

        self.test_sentence_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 15), wraplength=460, justify="center", padx=10, pady=5)
        self.test_sentence_label.grid(row=1, column=0, columnspan=2, pady=(0, 6))

        self.input_box = ctk.CTkEntry(self.frame, width=420, font=("Segoe UI", 14), corner_radius=20)
        self.input_box.grid(row=2, column=0, columnspan=2, pady=(20, 6))
        self.input_box.bind("<KeyRelease>", self.check_typing)
        self.input_box.bind("<Return>", self.finish_test)
        self.input_box.configure(state="disabled")

        self.feedback_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 13), wraplength=540, text_color="#ffffff")
        self.feedback_label.grid(row=3, column=0, columnspan=2, pady=(0, 2))

        self.timer_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 12), text_color="#aaaaaa")
        self.timer_label.grid(row=4, column=0, columnspan=2, pady=(0, 2))

        self.result_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 14, "bold"))
        self.result_label.grid(row=5, column=0, columnspan=2, pady=(4, 6))

        self.start_btn = self.styled_button(self.frame, "Start Test", self.start_test)
        self.start_btn.grid(row=6, column=0, pady=5, padx=5, sticky="e")

        self.practice_btn = self.styled_button(self.frame, "Practice Mode", self.start_practice)
        self.practice_btn.grid(row=6, column=1, pady=5, padx=5, sticky="w")

        self.best_btn = self.styled_button(self.frame, "Best Scores", self.show_scores)
        self.best_btn.grid(row=7, column=0, pady=5, padx=5, sticky="e")

        self.quit_btn = self.styled_button(self.frame, "Exit", self.root.destroy)
        self.quit_btn.configure(fg_color="#ff5e5e", hover_color="#e04848")
        self.quit_btn.grid(row=7, column=1, pady=5, padx=5, sticky="w")

    def start_test(self):
        self.practice_mode_on = False
        self.test_sentence = self.get_random_sentence()
        self.test_sentence_label.configure(text=self.test_sentence)
        self.input_box.configure(state="normal")
        self.input_box.delete(0, 'end')
        self.input_box.focus()
        self.feedback_label.configure(text="")
        self.result_label.configure(text="")
        self.start_time = time.time()
        self.timer_running = True
        threading.Thread(target=self.update_timer, daemon=True).start()

    def start_practice(self):
        self.practice_mode_on = True
        self.practice_sentence_count = 0
        self.practice_chars = 0
        self.practice_correct = 0
        self.practice_total = 0
        self.practice_start_time = time.time()
        self.next_practice_sentence()

    def next_practice_sentence(self):
        self.test_sentence = self.get_random_sentence()
        self.test_sentence_label.configure(text=self.test_sentence)
        self.input_box.configure(state="normal")
        self.input_box.delete(0, 'end')
        self.input_box.focus()
        self.feedback_label.configure(text="")
        self.result_label.configure(text="(Press Enter after each sentence)")

    def update_timer(self):
        while self.timer_running:
            elapsed = round(time.time() - self.start_time, 1)
            self.timer_label.configure(text=f"⏱ {elapsed}s")
            time.sleep(0.3)

    def check_typing(self, event=None):
        user_input = self.input_box.get()
        styled = ""

        for i, c in enumerate(self.test_sentence):
            if i < len(user_input):
                if user_input[i] == c:
                    styled += f"{c}"
                else:
                    styled += f"❌{c}"
            else:
                styled += c

        if len(user_input) > 0 and len(self.test_sentence) >= len(user_input):
            if user_input[-1] != self.test_sentence[len(user_input) - 1]:
                self.input_box.configure(border_color="red")
                self.root.after(200, lambda: self.input_box.configure(border_color="#3a7ebf"))

        self.feedback_label.configure(text=styled)

    def finish_test(self, event=None):
        user_input = self.input_box.get().strip()
        self.input_box.configure(state="disabled")

        if self.practice_mode_on:
            self.practice_sentence_count += 1
            self.practice_chars += len(user_input)
            self.practice_total += len(self.test_sentence)
            matcher = SequenceMatcher(None, self.test_sentence, user_input)
            correct = matcher.ratio() * len(self.test_sentence)
            self.practice_correct += correct
            self.next_practice_sentence()
            return

        if not self.timer_running:
            return

        self.timer_running = False
        end_time = time.time()

        time_taken = end_time - self.start_time
        wpm = self.calculate_wpm(len(user_input), time_taken)
        accuracy = self.calculate_accuracy(self.test_sentence, user_input)

        if wpm > self.best_scores["wpm"]:
            self.best_scores["wpm"] = wpm
        if accuracy > self.best_scores["accuracy"]:
            self.best_scores["accuracy"] = accuracy
        self.save_scores()

        self.result_label.configure(
            text=f"WPM: {wpm}    •    Accuracy: {accuracy}%",
            text_color="#44ff88"
        )
        self.input_box.configure(state="disabled")
        self.timer_label.configure(text="")

    def show_scores(self):
        if self.practice_mode_on:
            total_time = time.time() - self.practice_start_time
            avg_wpm = self.calculate_wpm(self.practice_chars, total_time)
            accuracy = (self.practice_correct / self.practice_total) * 100 if self.practice_total > 0 else 0

            self.result_label.configure(
                text=f"🔁 Practice Summary\nSentences: {self.practice_sentence_count}\nTime: {round(total_time)}s\nWPM: {round(avg_wpm, 2)}\nAccuracy: {round(accuracy, 2)}%",
                text_color="#ffaa00"
            )
            self.practice_mode_on = False
            self.input_box.configure(state="disabled")
            self.test_sentence_label.configure(text="")
            self.feedback_label.configure(text="")
            return

        self.test_sentence_label.configure(text="")
        self.result_label.configure(
            text=f"\n🏆 Best →\nWPM: {self.best_scores['wpm']}\nAccuracy: {self.best_scores['accuracy']}%",
            text_color="#00ccff"
        )
        self.feedback_label.configure(text="")
        self.timer_label.configure(text="")
        self.input_box.configure(state="disabled")


if __name__ == "__main__":
    root = ctk.CTk()
    app = TypingTestApp(root)
    root.mainloop()
