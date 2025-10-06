import pandas as pd
import google.generativeai as genai
import os

# --- Вставте ваші дані сюди ---
API_KEY = ""  # Замініть на ваш ключ
# ------------------------------------

def evaluate_student_answers(student_name, answers, model):
    """
    Sends all of a student's answers to the Gemini API for evaluation in a single request.
    """
    prompt_parts = [
        "Оціни відповіді студента на кожне запитання за 100-бальною шкалою за двома критеріями:\n"
        "1. **Правильність відповіді:** Наскільки точною та повною є відповідь?\n"
        "2. **Підозра на списування:** Чи не схожа відповідь на копію з Інтернету або надто формальний текст?\n\n"
        "Надай оцінку для кожної відповіді у форматі:\n"
        "**Запитання:** [Запитання]\n"
        "**Відповідь:** [Відповідь студента]\n"
        "**Правильність:** [оцінка від 0 до 100]\n"
        "**Підозра на списування:** [оцінка від 0 до 100, де 100 — дуже висока підозра]\n"
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

def main():
    """
    Main function to read student answers, evaluate them, and save the results.
    """
    try:
        print("▶️  Запуск скрипту...")

        if not API_KEY:
            raise ValueError("ПОМИЛКА: Будь ласка, вставте ваш API ключ у змінну API_KEY.")

        # 1. Конфігурація API
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name='gemini-2.5-pro')

        # 2. Читання файлу з відповідями
        try:
            df = pd.read_excel("test.xlsx")
        except FileNotFoundError:
            print("❌ ПОМИЛКА: Файл test.xlsx не знайдено.")
            return

        # 3. Підготовка до збереження результатів
        results = []
        question_columns = df.columns[4:]

        # 4. Оцінка відповідей
        for index, row in df.iterrows():
            student_name = row["Вкажіть прізвище та ім'я:"]
            print(f"\nОбробка відповідей для студента: {student_name}")

            student_answers = {}
            for question in question_columns:
                answer = row[question]
                if pd.notna(answer) and str(answer).strip():
                    student_answers[question] = str(answer)

            if not student_answers:
                continue

            print(f"  - Надсилання {len(student_answers)} відповідей на оцінку...")
            evaluation = evaluate_student_answers(student_name, student_answers, model)

            results.append({
                "Студент": student_name,
                "Запитання": "Всі запитання",
                "Відповідь": "\n\n".join([f"**{q}**:\n{a}" for q, a in student_answers.items()]),
                "Оцінка": evaluation
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