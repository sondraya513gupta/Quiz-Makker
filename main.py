import google.generativeai as genai
import re

# Set your Google API key
genai.configure(api_key="your api key")
def generate_quiz(topic, num_questions=5):
    """
    Generates a multiple-choice quiz based on the given topic.
    
    Args:
        topic (str): The topic for the quiz.
        num_questions (int): The number of questions to generate.
        
    Returns:
        list: A list of dictionaries containing questions, options, and the correct answer.
    """
    prompt = f"""
    Create a {num_questions}-question multiple-choice quiz on the topic "{topic}".
    Format each question exactly as follows (including the numbering):

    1. Question: [Your question here]
    A. [Option A]
    B. [Option B]
    C. [Option C]
    D. [Option D]
    Correct Answer: [A/B/C/D]

    2. Question: [Next question]
    [And so on...]
    """
    
    try:
        # Initialize the model with safety settings
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        model = genai.GenerativeModel("gemini-1.5-pro-latest",
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)
        
        response = model.generate_content(prompt)
        
        if not response:
            print("Error: No response received from the model")
            return []
            
        # Parse response
        quiz_text = response.text
        if not quiz_text:
            print("Error: Empty response received from the model")
            return []
        
        print("\nRaw response from model:")
        print(quiz_text)
        print("\nParsing questions...\n")
            
        questions = []
        # Split into individual questions using numbered pattern
        question_blocks = re.split(r'\n\d+\.', quiz_text)
        
        # Remove any empty blocks
        question_blocks = [block.strip() for block in question_blocks if block.strip()]
        
        for block in question_blocks:
            try:
                # Split the block into lines
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                
                # Extract question
                question = lines[0].split('Question:', 1)[1].strip()
                
                # Extract options
                options = {}
                for line in lines[1:5]:
                    if line.startswith(('A.', 'B.', 'C.', 'D.')):
                        key = line[0]
                        value = line[2:].strip()
                        options[key] = value
                
                # Extract correct answer
                correct_line = [l for l in lines if l.startswith('Correct Answer:')]
                if correct_line:
                    correct_answer = correct_line[0].split(':', 1)[1].strip()
                    
                    # Only add if we have all components
                    if question and len(options) == 4 and correct_answer:
                        questions.append({
                            "question": question,
                            "options": options,
                            "correct": correct_answer
                        })
                        print(f"Successfully parsed question {len(questions)}")
            except Exception as e:
                print(f"Error parsing question block: {str(e)}")
                continue
        
        if not questions:
            print("No valid questions could be parsed from the response")
        
        return questions
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def interactive_quiz(questions):
    """
    Conducts an interactive quiz session.
    
    Args:
        questions (list): A list of quiz questions in dictionary format.
    """
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}: {q['question']}")
        for option, text in q["options"].items():
            print(f"{option}. {text}")
        
        # Get the user's answer
        user_answer = input("Your answer (A, B, C, D): ").strip().upper()
        while user_answer not in q["options"]:
            user_answer = input("Invalid choice. Please enter A, B, C, or D: ").strip().upper()
        
        # Reveal the answer
        if user_answer == q["correct"]:
            print("✅ Correct!")
        else:
            print(f"❌ Incorrect. The correct answer was {q['correct']}.")

if __name__ == "__main__":
    print("Welcome to the Quiz Generator!")
    topic = input("Enter the topic for your quiz: ")
    num_questions = int(input("How many questions would you like? (1-10): "))
    
    # Validate number of questions
    if num_questions < 1 or num_questions > 10:
        print("Number of questions must be between 1 and 10. Setting to default 5.")
        num_questions = 5
    
    print(f"\nGenerating a {num_questions}-question quiz about {topic}...")
    questions = generate_quiz(topic, num_questions)
    
    if questions:
        print("\nQuiz generated successfully! Let's begin:")
        interactive_quiz(questions)
    else:
        print("Failed to generate quiz. Please try again.")
