print("🟢 ЗАПУСК ВЕРСІЇ 3.0 - ФІНАЛЬНА")
import csv
import requests
import os
import time

# --- НАЛАШТУВАННЯ ---
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
COL_GIT_NAME = 'git name'

def get_repo_column(fieldnames):
    if not fieldnames: return None
    if 'Repo Name' in fieldnames: return 'Repo Name'
    for col in fieldnames:
        # Шукаємо колонку з 3 цифр
        if col and str(col).strip().isdigit() and len(str(col).strip()) == 3:
            return col
    return None

def check_repo_exists(username, repo_name):
    if not username or not repo_name: return "EMPTY"
    url = f"https://github.com/{username}/{repo_name}"
    try:
        response = requests.get(url, timeout=5)
        return "OK" if response.status_code == 200 else "FAIL"
    except:
        return "ERROR"

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    if not os.path.exists(INPUT_DIR): 
        print("❌ Папка input не знайдена")
        return

    csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
    
    for filename in csv_files:
        print(f"\n📄 Обробка: {filename}")
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(input_path, mode='r', encoding='utf-8') as infile:
            # Чистимо файл від сміття
            clean_lines = (line.replace('\0','') for line in infile)
            reader = csv.DictReader(clean_lines)
            
            repo_col = get_repo_column(reader.fieldnames)
            
            if not repo_col:
                print("⚠️ Не знайдено колонку. Пропускаю.")
                continue

            print(f"   🎯 Колонка репозиторіїв: '{repo_col}'")
            
            # Якщо файл пустий або битий
            fieldnames = reader.fieldnames + ['Status'] if reader.fieldnames else ['Status']
            rows_to_write = []
            
            for row in reader:
                # --- ЗАХИСТ ВІД ПУСТОТИ (Те, чого не вистачало) ---
                raw_user = row.get(COL_GIT_NAME)
                raw_repo = row.get(repo_col)
                
                # Перетворюємо в стрічку примусово, навіть якщо там None
                git_user = str(raw_user if raw_user is not None else '').strip()
                repo_name = str(raw_repo if raw_repo is not None else '').strip()
                
                git_user = git_user.replace('_', '')
                
                status = "EMPTY"
                if git_user and repo_name:
                    status = check_repo_exists(git_user, repo_name)
                    print(f"   👉 {git_user} / {repo_name} -> {status}")
                
                if row:
                    row['Status'] = status
                    rows_to_write.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)

if __name__ == "__main__":
    main()
