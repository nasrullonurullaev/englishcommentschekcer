import os
import re
import subprocess
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Для детерминированности результатов langdetect
DetectorFactory.seed = 0

# Файлы, которые не проверяются (локализация, конфиги и т. д.)
EXCLUDED_FILES = (".json", ".yaml", ".yml", ".po", ".mo", ".xml")

# Регулярка для поиска комментариев (C++, Python, JS, Rust, Go и т. д.)
COMMENT_REGEX = re.compile(r"(?://|#|<!--|/\*|\*).+")

def get_diff():
    """Получает измененные строки в PR"""
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=0", "origin/main"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        print("❌ Ошибка при выполнении git diff")
        return ""

def extract_comments(diff_output):
    """Извлекает комментарии из измененных строк"""
    comments = []
    for line in diff_output.split("\n"):
        if line.startswith("+") and not line.startswith("+++") and COMMENT_REGEX.search(line):
            comments.append(line[1:].strip())  # Убираем "+"
    return comments

def detect_non_english_comments(comments):
    """Определяет язык комментария и фильтрует неанглийские"""
    non_english = []
    for comment in comments:
        try:
            lang = detect(comment)
            if lang != "en":
                non_english.append((comment, lang))
        except LangDetectException:
            continue
    return non_english

def main():
    diff_output = get_diff()
    if not diff_output:
        print("✅ Нет изменений для проверки")
        return

    comments = extract_comments(diff_output)
    if not comments:
        print("✅ В изменениях нет комментариев")
        return

    non_english_comments = detect_non_english_comments(comments)
    if non_english_comments:
        print("❌ Обнаружены комментарии не на английском языке:")
        for comment, lang in non_english_comments:
            print(f"- {comment} (определен язык: {lang})")
        exit(1)
    
    print("✅ Все комментарии на английском")

if __name__ == "__main__":
    main()
