import pandas as pd
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

# --- Вставте ваші дані сюди ---
load_dotenv()
API_KEY = os.getenv("API_KEY", "")  # Замініть на ваш ключ
# ------------------------------------

def evaluate_student_answers(student_name, answers, model):
    """
    Sends all of a student's answers to the Gemini API for evaluation in a single request.
    """
    prompt_parts = [
        "Проведи СУВОРУ оцінку відповідей студента на кожне запитання за 100-бальною шкалою. "
        "Будь особливо уважним до надто формальних відповідей або тих, що виглядають як копія з Інтернету — "
        "такі відповіді повинні отримувати високу оцінку за підозрою на списування та низьку за правильність.\n\n"
        "Оціни за двома критеріями:\n"
        "1. **Правильність відповіді:** Наскільки точною та повною є відповідь?\n"
        "2. **Підозра на списування:** Висока оцінка (90-100) означає пряме копіювання. Низька (0-10) — оригінальна відповідь.\n\n"
        "Надай оцінку для кожної відповіді у форматі:\n"
        "**Запитання:** [Запитання]\n"
        "**Відповідь:** [Відповідь студента]\n"
        "**Правильність:** [оцінка від 0 до 100]\n"
        "**Підозра на списування:** [оцінка від 0 до 100]\n"
        "**Коментар:** [коротке пояснення]\n"
        "---"
    ]

    for question, answer in answers.items():
        prompt_parts.append(f"**Запитання:** {question}\n**Відповідь:** {answer}\n")

    prompt = "\n".join(prompt_parts)

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Помилка під час звернення до API: {e}"

def parse_evaluation(evaluation_text):
    """
    Parses the evaluation text to extract total scores and comments for each question.
    """
    # Regex to find individual evaluation blocks
    evaluation_blocks = re.findall(r"\*\*Правильність:\*\* (\d+)\s*\n\s*\*\*Підозра на списування:\*\* (\d+)\s*\n\s*\*\*Коментар:\*\* (.*?)(?=\n---|\Z)", evaluation_text, re.DOTALL)

    total_correctness = 0
    total_suspicion = 0
    comments = []

    for i, block in enumerate(evaluation_blocks):
        correctness, suspicion, comment = block
        total_correctness += int(correctness)
        total_suspicion += int(suspicion)
        comments.append(f"Коментар до відповіді {i+1}: {comment.strip()}")

    return total_correctness, total_suspicion, "\n".join(comments)

def main():
    """
    Main function to read student answers, evaluate them, and save the results.
    """
    try:
        print("▶️  Запуск скрипту...")

        if not API_KEY:
            raise ValueError("ПОМИЛКА: Будь ласка, вставте ваш API ключ у файл .env.")

        # 1. Конфігурація API
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')

        # 2. Читання файлу з відповідями
        try:
            df = pd.read_excel("test.xlsx")
        except FileNotFoundError:
            print("❌ ПОМИЛКА: Файл test.xlsx не знайдено.")
            return

        # 3. Підготовка до збереження результатів
        results = []
        question_columns = df.columns[4:]
        num_questions = len(question_columns)

        # 4. Оцінка відповідей
        for index, row in df.iterrows():
            student_name = row["Вкажіть прізвище та ім'я:"]
            print(f"\nОбробка відповідей для студента: {student_name}")

            student_answers = {}
            for question in question_columns:
                answer = row[question]
                if pd.notna(answer) and str(answer).strip():
                    student_answers[question] = str(answer)

            total_correctness = 0
            total_suspicion = 0
            comments = "Студент не надав жодної відповіді."

            if student_answers:
                print(f"  - Надсилання {len(student_answers)} відповідей на оцінку...")
                evaluation_raw = evaluate_student_answers(student_name, student_answers, model)
                total_correctness, total_suspicion, comments = parse_evaluation(evaluation_raw)

            # Calculate averages based on the total number of questions
            avg_correctness = total_correctness / num_questions if num_questions > 0 else 0
            avg_suspicion = total_suspicion / num_questions if num_questions > 0 else 0

            results.append({
                "Номер студента": index + 1,
                "Студент": student_name,
                "Коментарі з оцінки": comments,
                "Середня правильність": avg_correctness,
                "Середня підозра": avg_suspicion
            })

        # 5. Збереження результатів у новий файл
        if results:
            results_df = pd.DataFrame(results)
            results_df.to_excel("results.xlsx", index=False)
            print("\n✅ Результати збережено у файлі results.xlsx")
        else:
            print("\n⚠️ Не знайдено відповідей для оцінки.")

    except Exception as e:
        print(f"\n❌ СТАЛАСЯ ПОМИЛКА: {e}")

    finally:
        print("\n=============================================")
        input("Натисніть Enter, щоб закрити це вікно.")

if __name__ == "__main__":
    main()