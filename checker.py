import csv
import requests
import os
import time

# --- НАЛАШТУВАННЯ ---
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
COL_GIT_NAME = 'git name'

def get_repo_column(fieldnames):
    """
    Шукає колонку з назвою репозиторію.
    Пріоритет: 
    1. Точна назва 'Repo Name'
    2. Номер групи (наприклад '401', '402')
    """
    # Варіант 1: Стандартна назва
    if 'Repo Name' in fieldnames:
        return 'Repo Name'
    
    # Варіант 2: Шукаємо колонку, яка складається з 3 цифр (401, 402...)
    for col in fieldnames:
        if col.strip().isdigit() and len(col.strip()) == 3:
            return col
            
    return None

def check_repo_exists(username, repo_name):
    url = f"https://github.com/{username}/{repo_name}"
    try:
        response = requests.get(url, timeout=5)
        return "OK" if response.status_code == 200 else "FAIL"
    except:
        return "ERROR"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(INPUT_DIR):
        print("❌ Папка input не знайдена")
        return

    csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
    
    for filename in csv_files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"\n📄 Обробка: {filename}")
        
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # --- РОЗУМНИЙ ПОШУК КОЛОНКИ ---
            repo_col = get_repo_column(fieldnames)
            
            if not repo_col:
                print(f"⚠️ У файлі немає колонки 'Repo Name' або номера групи (401, 402...). Пропускаю.")
                continue
                
            print(f"   🎯 Знайдено колонку з репозиторіями: '{repo_col}'")

            # Додаємо статус
            out_fieldnames = fieldnames + ['Status']
            rows_to_write = []
            
            for row in reader:
                git_user = row.get(COL_GIT_NAME, '').strip()
                repo_name = row.get(repo_col, '').strip()
                
                if git_user and repo_name:
                    # Валідація нікнейму (прибираємо заборонені символи, якщо раптом є)
                    git_user = git_user.replace('_', '') 
                    status = check_repo_exists(git_user, repo_name)
                    print(f"   👉 {git_user}/{repo_name} -> {status}")
                else:
                    status = "EMPTY"
                
                row['Status'] = status
                rows_to_write.append(row)
                time.sleep(0.1) 

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)

if __name__ == "__main__":
    main()
