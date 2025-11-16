import json
import os
import glob
import random

def load_questions(filename):
    """Load questions from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("questions", [])
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{filename}'!")
        return []

def display_question(question_data, question_num, total):
    """Display a question with its options."""
    print(f"\n{'='*60}")
    print(f"Question {question_num}/{total}")
    print(f"{'='*60}")
    print(f"\n{question_data['question']}\n")
    
    options = question_data['options']
    for i, option in enumerate(options):
        print(f"  {i + 1}. {option}")
    
    print()

def get_user_answer(num_options):
    """Get and validate user's answer."""
    while True:
        try:
            answer = input(f"Enter your answer (1-{num_options}): ").strip()
            answer_num = int(answer)
            if 1 <= answer_num <= num_options:
                return answer_num - 1  # Convert to 0-based index
            else:
                print(f"Please enter a number between 1 and {num_options}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nQuiz cancelled by user.")
            return None

def run_quiz(questions):
    """Run the quiz and return the score."""
    if not questions:
        print("No questions available!")
        return
    
    total_questions = len(questions)
    correct_answers = 0
    incorrect_answers = []
    
    print("\n" + "="*60)
    print("WELCOME TO THE MCQ QUIZ!")
    print("="*60)
    print(f"Total questions: {total_questions}")
    print("="*60)
    
    for i, question_data in enumerate(questions, 1):
        display_question(question_data, i, total_questions)
        
        user_answer = get_user_answer(len(question_data['options']))
        
        if user_answer is None:  # User cancelled
            return
        
        correct_index = question_data['correct_answer']
        
        if user_answer == correct_index:
            print("✓ Correct!")
            correct_answers += 1
        else:
            correct_option = question_data['options'][correct_index]
            print(f"✗ Incorrect. The correct answer is: {correct_option}")
            incorrect_answers.append({
                'question_num': i,
                'question': question_data['question'],
                'your_answer': question_data['options'][user_answer],
                'correct_answer': correct_option
            })
    
    # Display results
    print("\n" + "="*60)
    print("QUIZ RESULTS")
    print("="*60)
    print(f"Total Questions: {total_questions}")
    print(f"Correct Answers: {correct_answers}")
    print(f"Incorrect Answers: {total_questions - correct_answers}")
    print(f"Score: {correct_answers}/{total_questions} ({correct_answers/total_questions*100:.1f}%)")
    print("="*60)
    
    if incorrect_answers:
        print("\nQuestions you got wrong:")
        print("-"*60)
        for item in incorrect_answers:
            print(f"\nQuestion {item['question_num']}: {item['question']}")
            print(f"  Your answer: {item['your_answer']}")
            print(f"  Correct answer: {item['correct_answer']}")
    
    return correct_answers, total_questions

def find_lecture_files():
    """Find all lecture JSON files in the current directory."""
    files = sorted(glob.glob("lecture*.json"))
    return files

def get_lecture_info():
    """Get information about all available lectures."""
    lecture_files = find_lecture_files()
    lecture_info = []
    
    for filename in lecture_files:
        questions = load_questions(filename)
        if questions:
            lecture_info.append({
                'filename': filename,
                'name': filename.replace('.json', '').replace('_', ' ').title(),
                'count': len(questions)
            })
    
    return lecture_info

def select_questions_evenly(lecture_info, total_questions=40):
    """Select questions evenly distributed across all lectures."""
    all_questions = []
    
    # Load all questions with their source lecture
    for info in lecture_info:
        questions = load_questions(info['filename'])
        # Create a copy of each question with source lecture info
        for q in questions:
            q_copy = q.copy()
            q_copy['source_lecture'] = info['name']
            all_questions.append(q_copy)
    
    if not all_questions:
        return []
    
    # Calculate how many questions per lecture (base allocation)
    num_lectures = len(lecture_info)
    base_per_lecture = total_questions // num_lectures
    remainder = total_questions % num_lectures
    
    selected = []
    
    # Allocate questions evenly across lectures
    for info in lecture_info:
        questions = [q for q in all_questions if q.get('source_lecture') == info['name']]
        if not questions:
            continue
        
        # How many to take from this lecture
        count = base_per_lecture
        if remainder > 0:
            count += 1
            remainder -= 1
        
        # Don't take more than available
        count = min(count, len(questions))
        
        # Randomly select questions from this lecture
        if count > 0:
            selected_from_lecture = random.sample(questions, count)
            selected.extend(selected_from_lecture)
    
    # Shuffle the final selection
    random.shuffle(selected)
    
    # Remove the source_lecture metadata before returning
    for q in selected:
        q.pop('source_lecture', None)
    
    return selected

def display_menu(lecture_info):
    """Display menu and get user selection."""
    print("\n" + "="*60)
    print("PHILOSOPHY QUIZ - SELECT MODE")
    print("="*60)
    print("\nAvailable Lectures:")
    print("-"*60)
    
    for i, info in enumerate(lecture_info, 1):
        print(f"  {i}. {info['name']} ({info['count']} questions)")
    
    print(f"\n  {len(lecture_info) + 1}. Final Check (40 questions, evenly distributed)")
    print("  0. Exit")
    print("-"*60)
    
    while True:
        try:
            choice = input(f"\nEnter your choice (0-{len(lecture_info) + 1}): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return None, "exit"
            elif 1 <= choice_num <= len(lecture_info):
                selected_info = lecture_info[choice_num - 1]
                return selected_info['filename'], "lecture"
            elif choice_num == len(lecture_info) + 1:
                return None, "final"
            else:
                print(f"Please enter a number between 0 and {len(lecture_info) + 1}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nQuiz cancelled by user.")
            return None, "exit"

def main():
    """Main function to run the quiz."""
    # Find all lecture files
    lecture_info = get_lecture_info()
    
    if not lecture_info:
        print("Error: No lecture files found!")
        print("Please ensure lecture*.json files exist in the current directory.")
        return
    
    # Display menu and get selection
    selection, mode = display_menu(lecture_info)
    
    if mode == "exit":
        print("Goodbye!")
        return
    
    questions = []
    
    if mode == "lecture":
        # Load questions from selected lecture
        questions = load_questions(selection)
        if not questions:
            print(f"No questions loaded from {selection}.")
            return
    elif mode == "final":
        # Select 40 questions evenly distributed
        print("\n" + "="*60)
        print("FINAL CHECK MODE")
        print("="*60)
        print("Selecting 40 questions evenly distributed across all lectures...")
        questions = select_questions_evenly(lecture_info, total_questions=40)
        
        if not questions:
            print("Error: Could not select questions for final check.")
            return
        
        print(f"Selected {len(questions)} questions from all lectures.")
    
    # Run the quiz
    if questions:
        run_quiz(questions)
    else:
        print("No questions available.")

if __name__ == "__main__":
    main()

