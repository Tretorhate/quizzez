import json
import os
import glob
import random
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SUBJECTS = [
    {
        'key': 'philosophy',
        'name': 'Philosophy',
        'directory': os.path.join(BASE_DIR, 'phylosophy'),
        'extra_files': []
    },
    {
        'key': 'computer_networks',
        'name': 'Computer Networks',
        'directory': os.path.join(BASE_DIR, 'computer_networks'),
        'extra_files': [
            os.path.join(BASE_DIR, 'computer_networks', 'provided_CN.json')
        ]
    }
]

def load_questions(filename):
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

def display_question(question_data, question_num, total, options):
    print(f"\n{'='*60}")
    print(f"Question {question_num}/{total}")
    print(f"{'='*60}")
    print(f"\n{question_data['question']}\n")
    
    for i, option in enumerate(options):
        print(f"  {i + 1}. {option}")
    
    print()

def get_user_answer(num_options):
    while True:
        try:
            answer = input(f"Enter your answer (1-{num_options}): ").strip()
            answer_num = int(answer)
            if 1 <= answer_num <= num_options:
                return answer_num - 1
            else:
                print(f"Please enter a number between 1 and {num_options}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nQuiz cancelled by user.")
            return None

def shuffle_question_options(question_data):
    indexed_options = list(enumerate(question_data['options']))
    random.shuffle(indexed_options)
    
    shuffled_options = [option for _, option in indexed_options]
    correct_index = next(
        i for i, (original_index, _) in enumerate(indexed_options)
        if original_index == question_data['correct_answer']
    )
    return shuffled_options, correct_index

def run_quiz(questions):
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
        shuffled_options, correct_index = shuffle_question_options(question_data)
        display_question(question_data, i, total_questions, shuffled_options)
        
        user_answer = get_user_answer(len(shuffled_options))
        
        if user_answer is None:
            return
        
        if user_answer == correct_index:
            print("✓ Correct!")
            correct_answers += 1
        else:
            correct_option = shuffled_options[correct_index]
            print(f"✗ Incorrect. The correct answer is: {correct_option}")
            incorrect_answers.append({
                'question_num': i,
                'question': question_data['question'],
                'your_answer': shuffled_options[user_answer],
                'correct_answer': correct_option
            })
    
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

LECTURE_FILENAME_RE = re.compile(r'^lecture(\d+)(?:_(\d+))?$', re.IGNORECASE)

def lecture_sort_key(filepath):
    base = os.path.splitext(os.path.basename(filepath))[0]
    match = LECTURE_FILENAME_RE.match(base)
    if match:
        primary = int(match.group(1))
        secondary = int(match.group(2)) if match.group(2) else 0
        return (primary, secondary, base.lower())
    return (float('inf'), float('inf'), base.lower())

def find_lecture_files(directory):
    pattern = os.path.join(directory, "lecture*.json")
    files = sorted(glob.glob(pattern), key=lecture_sort_key)
    return files

def get_lecture_info(directory, extra_files=None):
    lecture_files = find_lecture_files(directory)
    if extra_files:
        for filepath in extra_files:
            full_path = filepath if os.path.isabs(filepath) else os.path.join(directory, filepath)
            if os.path.exists(full_path) and full_path not in lecture_files:
                lecture_files.append(full_path)
    lecture_info = []
    
    for filename in lecture_files:
        questions = load_questions(filename)
        if questions:
            lecture_info.append({
                'filename': filename,
                'name': os.path.splitext(os.path.basename(filename))[0].replace('_', ' ').title(),
                'count': len(questions)
            })
    
    return lecture_info

def select_questions_evenly(lecture_info, total_questions=40):
    all_questions = []
    
    for info in lecture_info:
        questions = load_questions(info['filename'])
        for q in questions:
            q_copy = q.copy()
            q_copy['source_lecture'] = info['name']
            all_questions.append(q_copy)
    
    if not all_questions:
        return []
    
    num_lectures = len(lecture_info)
    base_per_lecture = total_questions // num_lectures
    remainder = total_questions % num_lectures
    
    selected = []
    
    for info in lecture_info:
        questions = [q for q in all_questions if q.get('source_lecture') == info['name']]
        if not questions:
            continue
        
        count = base_per_lecture
        if remainder > 0:
            count += 1
            remainder -= 1
        
        count = min(count, len(questions))
        
        if count > 0:
            selected_from_lecture = random.sample(questions, count)
            selected.extend(selected_from_lecture)
    
    random.shuffle(selected)
    
    for q in selected:
        q.pop('source_lecture', None)
    
    return selected

def display_subject_menu():
    print("\n" + "="*60)
    print("SELECT SUBJECT")
    print("="*60)
    
    for i, subject in enumerate(SUBJECTS, 1):
        print(f"  {i}. {subject['name']}")
    print("  0. Exit")
    
    while True:
        try:
            choice = input(f"\nEnter your choice (0-{len(SUBJECTS)}): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return None
            elif 1 <= choice_num <= len(SUBJECTS):
                return SUBJECTS[choice_num - 1]
            else:
                print(f"Please enter a number between 0 and {len(SUBJECTS)}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nQuiz cancelled by user.")
            return None

def display_menu(lecture_info, subject_name):
    print("\n" + "="*60)
    print(f"{subject_name.upper()} QUIZ - SELECT MODE")
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
    subject = display_subject_menu()
    
    if subject is None:
        print("Goodbye!")
        return
    
    subject_dir = subject['directory']
    subject_name = subject['name']
    
    if not os.path.isdir(subject_dir):
        print(f"Error: Subject directory '{subject_dir}' not found!")
        return
    
    lecture_info = get_lecture_info(subject_dir, subject.get('extra_files'))
    
    if not lecture_info:
        print("Error: No lecture files found!")
        print("Please ensure lecture*.json files exist in the selected subject directory.")
        return
    
    selection, mode = display_menu(lecture_info, subject_name)
    
    if mode == "exit":
        print("Goodbye!")
        return
    
    questions = []
    
    if mode == "lecture":
        questions = load_questions(selection)
        if not questions:
            print(f"No questions loaded from {selection}.")
            return
    elif mode == "final":
        print("\n" + "="*60)
        print("FINAL CHECK MODE")
        print("="*60)
        print("Selecting 40 questions evenly distributed across all lectures...")
        questions = select_questions_evenly(lecture_info, total_questions=40)
        
        if not questions:
            print("Error: Could not select questions for final check.")
            return
        
        print(f"Selected {len(questions)} questions from all lectures.")
    
    if questions:
        run_quiz(questions)
    else:
        print("No questions available.")

if __name__ == "__main__":
    main()

