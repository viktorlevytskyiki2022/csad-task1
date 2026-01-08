import csv
import requests
import os
import time

# --- НАЛАШТУВАННЯ ---
INPUT_DIR = 'input'    # Папка, куди Google Script кидає CSV
OUTPUT_DIR = 'output'  # Папка, куди ми покладемо результат
# Назви колонок у CSV (мають точно співпадати з тими, що в таблиці!)
COL_GIT_NAME = 'git name'   # Нікнейм студента
COL_REPO_NAME = '402' # Назва репозиторію (згенерував викладач формулою)

def check_repo_exists(username, repo_name):
    """Перевіряє, чи існує публічний репозиторій на GitHub."""
    # Формуємо посилання: https://github.com/user/repo
    url = f"https://github.com/{username}/{repo_name}"
    try:
        # Робимо запит. timeout=5 означає чекати не більше 5 сек
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return "OK"   # Репозиторій є і він публічний
        elif response.status_code == 404:
            return "FAIL" # Такого репозиторію немає
        else:
            return f"ERR:{response.status_code}" # Інша помилка
    except Exception as e:
        return "ERROR" # Помилка з'єднання

def main():
    # 1. Створюємо папку output, якщо її немає
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Створено папку {OUTPUT_DIR}")

    # 2. Шукаємо CSV файли в папці input
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Помилка: Папка '{INPUT_DIR}' не знайдена. Запустіть спочатку експорт з Google Таблиці.")
        return

    csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
    
    if not csv_files:
        print("⚠️ У папці input немає CSV файлів.")
        return

    print(f"🔍 Знайдено файлів: {len(csv_files)}")

    # 3. Обробляємо кожен файл
    for filename in csv_files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"\n📄 Обробка файлу: {filename}...")
        
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Перевіряємо, чи є потрібні колонки
            if COL_GIT_NAME not in reader.fieldnames or COL_REPO_NAME not in reader.fieldnames:
                print(f"❌ Пропускаю файл, бо немає колонок '{COL_GIT_NAME}' або '{COL_REPO_NAME}'")
                continue

            # Додаємо нову колонку Status
            fieldnames = reader.fieldnames + ['Status']
            
            rows_to_write = []
            
            for row in reader:
                git_user = row.get(COL_GIT_NAME, '').strip()
                repo_name = row.get(COL_REPO_NAME, '').strip()
                
                # Перевіряємо тільки якщо є дані
                if git_user and repo_name:
                    status = check_repo_exists(git_user, repo_name)
                    print(f"   👉 {git_user}/{repo_name} -> {status}")
                else:
                    status = "EMPTY"
                
                row['Status'] = status
                rows_to_write.append(row)
                
                # Маленька пауза, щоб GitHub не заблокував за спам запитами
                time.sleep(0.2) 

        # 4. Записуємо результат у новий файл
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
        print(f"✅ Результат збережено: {output_path}")

if __name__ == "__main__":
    main()
