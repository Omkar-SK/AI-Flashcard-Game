import tkinter as tk
from tkinter import messagebox
import json
import random
from datetime import datetime

# File for saving flashcards
FLASHCARDS_FILE = "flashcards.json"

# Load flashcards from the JSON file
def load_flashcards():
    try:
        with open(FLASHCARDS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save flashcards to the JSON file
def save_flashcards(flashcards):
    with open(FLASHCARDS_FILE, "w") as file:
        json.dump(flashcards, file)

# Calculate flashcard priority based on mastery level and review history
def calculate_card_priority(card):
    current_time = datetime.now().timestamp()
    last_reviewed = card.get('last_reviewed', 0)
    time_since_review = current_time - last_reviewed

    intervals = [1, 3, 7, 14, 20, 30, 45]
    review_interval = intervals[min(card.get('mastery_level', 0), len(intervals) - 1)]
    priority = (
        (time_since_review / (review_interval * 60)) +
        (5 - min(card.get('mastery_level', 5), 5)) * 2 +
        card.get('incorrect_count', 0) * 1.5
    )
    return priority

# Select the next flashcard based on priority
def select_next_flashcard(flashcards):
    if not flashcards:
        return None

    cards_with_priority = [
        (card, calculate_card_priority(card))
        for card in flashcards
    ]
    cards_with_priority.sort(key=lambda x: x[1], reverse=True)
    top_cards = cards_with_priority[:3]
    return random.choice(top_cards)[0]

# Updated start_quiz function with "End Quiz" functionality
def start_quiz():
    if not flashcards:
        messagebox.showwarning("No Flashcards", "Please add some flashcards first!")
        return

    quiz_window = tk.Toplevel(root)
    quiz_window.title("Quiz")
    quiz_window.geometry("500x400")
    quiz_window.configure(bg="#f1f3f4")
  
    current_card = {"data": None}
    correct_count = {"value": 0}
    wrong_count = {"value": 0}

    def load_next_flashcard():
        current_card["data"] = select_next_flashcard(flashcards)
        if current_card["data"]:
            question_label.config(text=current_card["data"]["question"])
            answer_var.set("")
            result_label.config(text="")
            answer_entry.focus()  # Set focus to answer entry for immediate typing
        else:
            question_label.config(text="No more flashcards available!")
            submit_button.config(state="disabled")
            answer_entry.config(state="disabled")

    def check_answer(event=None):  # Added event parameter to handle both button and Enter key
        user_answer = answer_var.get().strip()
        current_time = datetime.now().timestamp()

        if user_answer.lower() == current_card["data"]["answer"].lower():
            result_label.config(text="Correct!", fg="#198754")  # Green for correct answer
            current_card["data"]["mastery_level"] += 1
            current_card["data"]["last_reviewed"] = current_time
            correct_count["value"] += 1
        else:
            result_label.config(
                text=f"Incorrect! Correct Answer: {current_card['data']['answer']}",
                fg="#dc3545",  # Red for incorrect answer
            )
            current_card["data"]["incorrect_count"] += 1
            wrong_count["value"] += 1

        # Update score display
        score_label.config(
            text=f"Correct: {correct_count['value']} | Wrong: {wrong_count['value']}"
        )
        save_flashcards(flashcards)

        # Automatically load the next flashcard
        quiz_window.after(1500, load_next_flashcard)  # Add delay for feedback visibility

    def end_quiz():
        messagebox.showinfo(
            "Quiz Ended",
            f"Quiz ended!\nFinal Score:\nCorrect: {correct_count['value']}\nWrong: {wrong_count['value']}",
        )
        quiz_window.destroy()

    question_label = tk.Label(quiz_window, text="", font=("Arial", 14), bg="#f1f3f4")
    question_label.pack(pady=20)

    answer_var = tk.StringVar()
    answer_entry = tk.Entry(quiz_window, textvariable=answer_var, font=("Arial", 12), width=40)
    answer_entry.pack(pady=10)
    answer_entry.bind('<Return>', check_answer)  # Bind Enter key to check_answer
    answer_entry.focus()  # Set initial focus to answer entry

    result_label = tk.Label(quiz_window, text="", font=("Arial", 12), bg="#f1f3f4")
    result_label.pack(pady=10)

    score_label = tk.Label(
        quiz_window,
        text=f"Correct: {correct_count['value']} | Wrong: {wrong_count['value']}",
        font=("Arial", 12),
        bg="#f1f3f4",
        fg="#212529",
    )
    score_label.pack(pady=10)

    submit_button = tk.Button(
        quiz_window,
        text="Submit",
        command=check_answer,
        font=("Arial", 12),
        bg="#0d6efd",
        fg="white",
    )
    submit_button.pack(pady=10)

    end_button = tk.Button(
        quiz_window,
        text="End Quiz",
        command=end_quiz,
        font=("Arial", 12),
        bg="#dc3545",
        fg="white",
    )
    end_button.pack(pady=10)

    load_next_flashcard()

# Add a new flashcard
def add_flashcard():
    question_window = tk.Toplevel(root)
    question_window.title("Add Flashcard")
    question_window.geometry("400x300")
    question_window.configure(bg="#f8f9fa")
    
    tk.Label(question_window, text="Enter the question:", font=("Arial", 12), bg="#f8f9fa").pack(pady=10)
    question_entry = tk.Entry(question_window, font=("Arial", 12), width=40)
    question_entry.pack(pady=5)

    tk.Label(question_window, text="Enter the answer:", font=("Arial", 12), bg="#f8f9fa").pack(pady=10)
    answer_entry = tk.Entry(question_window, font=("Arial", 12), width=40)
    answer_entry.pack(pady=5)

    def save_card():
        question = question_entry.get().strip()
        answer = answer_entry.get().strip()
        if question and answer:
            new_card = {
                "question": question,
                "answer": answer,
                "mastery_level": 0,
                "incorrect_count": 0,
                "last_reviewed": 0,
            }
            flashcards.append(new_card)
            save_flashcards(flashcards)
            messagebox.showinfo("Success", "Flashcard added successfully!")
            question_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Both question and answer are required!")

    tk.Button(question_window, text="Save Flashcard", command=save_card, font=("Arial", 12), bg="#198754", fg="white").pack(pady=20)

# View all flashcards
def view_flashcards():
    flashcard_window = tk.Toplevel(root)
    flashcard_window.title("View Flashcards")
    flashcard_window.geometry("450x350")
    flashcard_window.configure(bg="#ffffff")
    
    if not flashcards:
        tk.Label(flashcard_window, text="No flashcards available.", font=("Arial", 14), bg="#ffffff", fg="#6c757d").pack(pady=20)
        return

    # Create main frame
    main_frame = tk.Frame(flashcard_window, bg="#ffffff")
    main_frame.pack(fill="both", expand=True)

    # Create canvas
    canvas = tk.Canvas(main_frame, bg="#ffffff", borderwidth=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#ffffff")

    # Configure the canvas
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Mouse wheel scrolling functions
    def on_mousewheel(event):
        # For Windows and MacOS
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_mousewheel_linux(event):
        # For Linux
        if event.num == 4:  # Scroll up
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Scroll down
            canvas.yview_scroll(1, "units")

    # Bind mouse wheel events
    canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows and MacOS
    canvas.bind_all("<Button-4>", on_mousewheel_linux)  # Linux scroll up
    canvas.bind_all("<Button-5>", on_mousewheel_linux)  # Linux scroll down

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Add flashcards to the scroll frame
    for card in flashcards:
        card_frame = tk.Frame(scroll_frame, bg="#f8f9fa", bd=1, relief="solid")
        card_frame.pack(pady=5, padx=10, fill="x")
        
        tk.Label(
            card_frame,
            text=f"Q: {card['question']}\nA: {card['answer']}\nMastery Level: {card.get('mastery_level', 0)}",
            font=("Arial", 10),
            bg="#f8f9fa",
            fg="#212529",
            anchor="w",
            justify="left",
            padx=10,
            pady=5
        ).pack(fill="x")

    # Cleanup function to remove bindings when window is closed
    def on_closing():
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        flashcard_window.destroy()

    flashcard_window.protocol("WM_DELETE_WINDOW", on_closing)

# Main application window
root = tk.Tk()
root.title("MindMatrix - Intelligent Flashcard game for Revision")
root.geometry("500x400")
root.configure(bg="#ADD8E6")

flashcards = load_flashcards()

tk.Label(root, text="MindMatrix", font=("Arial", 16, "bold"), bg="#ffffff", fg="#0d6efd").pack(pady=100)
tk.Button(root, text="Start Quiz", command=start_quiz, font=("Arial", 12), bg="#0d6efd", fg="white").pack(pady=10)
tk.Button(root, text="Add Flashcard", command=add_flashcard, font=("Arial", 12), bg="#198754", fg="white").pack(pady=10)
tk.Button(root, text="View Flashcards", command=view_flashcards, font=("Arial", 12), bg="#ffc107", fg="white").pack(pady=10)
tk.Label(root, text="Keep Learning!", font=("Arial", 10), bg="#ffffff", fg="#6c757d").pack(pady=20)

root.mainloop()