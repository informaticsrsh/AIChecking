import google.generativeai as genai

# --- Вставте ваші дані сюди ---
API_KEY = ""  # Замініть на ваш ключ
TOPIC = "Майбутнє штучного інтелекту в медицині" # Замініть на вашу тему
# ------------------------------------

try:
    print("▶️  Запуск скрипту...")
    
    if "YOUR_GEMINI_API_KEY" in API_KEY or not API_KEY:
        raise ValueError("ПОМИЛКА: Будь ласка, вставте ваш API ключ у змінну API_KEY.")

    # 1. Конфігурація API
    genai.configure(api_key=API_KEY)

    # 2. Створення моделі (використовуємо найнадійнішу 'gemini-pro')
    # Модель 'gemini-1.5-flash' може бути недоступна в деяких регіонах
    print("🤖 Створення моделі gemini-pro...")
    model = genai.GenerativeModel(model_name='gemini-2.5-pro')

    # 3. Створення запиту
    prompt = f"Напиши текст приблизно на 500 символів українською мовою на тему: '{TOPIC}'"
    
    # 4. Генерація контенту
    print("💬 Надсилання запиту до Gemini...")
    response = model.generate_content(prompt)

    # 5. Виведення результату
    print("\n✅ Згенерований текст:\n---")
    print(response.text)
    print("---")

except Exception as e:
    print(f"\n❌ СТАЛАСЯ ПОМИЛКА: {e}")

finally:
    print("\n=============================================")
    input("Натисніть Enter, щоб закрити це вікно.")