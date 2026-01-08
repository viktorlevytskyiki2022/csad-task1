print("🟢 ЗАПУСК ВЕРСІЇ 4.0 - РОЗУМНИЙ ПОШУК КОЛОНОК")
import csv
import requests
import os
import time

# --- НАЛАШТУВАННЯ ---
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

def find_column_by_keyword(fieldnames, keywords):
    """Шукає колонку, яка містить одне з ключових слів (ігноруючи регістр)"""
    if not fieldnames: return None
    
    # 1. Спробуємо точний збіг
    for kw in keywords:
        if kw in fieldnames: return kw
        
    # 2. Спробуємо неточний збіг (шукаємо слово всередині)
    for col in fieldnames:
        clean_col = str(col).lower().strip()
        for kw in keywords:
            if kw.lower() in clean_col:
                return col
    return None

def check_repo_exists(username, repo_name):
    if not username or not repo_name: return "EMPTY"
    # Очищаємо від можливих пробілів
    username = username.strip()
    repo_name = repo_name.strip()
    
    url = f"https://github.com/{username}/{repo_name}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "OK"
        else:
            return "FAIL" # (код 404)
    except:
        return "ERROR"

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR): return

    csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
    
    for filename in csv_files:
        print(f"\n📄 Обробка: {filename}")
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(input_path, mode='r', encoding='utf-8') as infile:
            # Чистимо файл від "сміття"
            clean_lines = (line.replace('\0','') for line in infile)
            reader = csv.DictReader(clean_lines)
            fieldnames = reader.fieldnames
            
            # --- РОЗУМНИЙ ПОШУК КОЛОНОК ---
            # Шукаємо колонку де є слово "git"
            git_col = find_column_by_keyword(fieldnames, ['git name', 'git', 'github'])
            # Шукаємо колонку де є "402" або "Repo Name"
            repo_col = find_column_by_keyword(fieldnames, ['402', 'Repo Name', 'repo'])
            
            print(f"   🎯 Колонка Git: '{git_col}'")
            print(f"   🎯 Колонка Repo: '{repo_col}'")
            
            if not repo_col:
                print("⚠️ Не знайшов колонку з репозиторієм. Пропускаю.")
                continue

            # Готуємо заголовки
            new_fieldnames = fieldnames + ['Status']
            rows_to_write = []
            
            for row in reader:
                # Дістаємо дані "безпечно"
                raw_user = row.get(git_col) if git_col else ''
                raw_repo = row.get(repo_col) if repo_col else ''
                
                git_user = str(raw_user if raw_user else '').strip()
                repo_name = str(raw_repo if raw_repo else '').strip()
                
                # Статус за замовчуванням
                status = "EMPTY"
                
                # Перевіряємо ТІЛЬКИ якщо є і юзер, і репо
                if len(git_user) > 1 and len(repo_name) > 1:
                    status = check_repo_exists(git_user, repo_name)
                    print(f"   👉 Перевірка: {git_user} / {repo_name} -> {status}")
                
                # Зберігаємо результат
                if row:
                    row['Status'] = status
                    rows_to_write.append(row)

        # Записуємо новий файл
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)

if __name__ == "__main__":
    main()
