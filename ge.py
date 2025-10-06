import pandas as pd
import google.generativeai as genai
import os

# --- Вставте ваші дані сюди ---
API_KEY = ""  # Замініть на ваш ключ
# ------------------------------------

def evaluate_answer(question, answer, model):
    """
    Sends a student's answer to the Gemini API for evaluation.
    """
    prompt = f"""
    Оціни відповідь студента на запитання за 100-бальною шкалою за двома критеріями:
    1.  **Правильність відповіді:** Наскільки точною та повною є відповідь?
    2.  **Підозра на списування:** Чи не схожа відповідь на копію з Інтернету або надто формальний текст?

    **Запитання:** {question}
    **Відповідь студента:** {answer}

    Надай оцінку у форматі:
    **Правильність:** [оцінка від 0 до 100]
    **Підозра на списування:** [оцінка від 0 до 100, де 100 — дуже висока підозра]
    **Коментар:** [коротке пояснення]
    """
    
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
        model = genai.GenerativeModel(model_name='gemini-pro')

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

            for question in question_columns:
                answer = row[question]

                # Пропускаємо порожні відповіді
                if pd.isna(answer) or not str(answer).strip():
                    continue

                print(f"  - Оцінка відповіді на запитання: '{question}'")
                evaluation = evaluate_answer(question, answer, model)

                results.append({
                    "Студент": student_name,
                    "Запитання": question,
                    "Відповідь": answer,
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