import os
import re
import subprocess

# File extensions to exclude (локализация, конфиги и т.д.)
EXCLUDED_FILES = (".json", ".yaml", ".yml", ".po", ".mo", ".xml")

# Регулярка для поиска комментариев (Python, C++, JS, Rust, Go и т.д.)
COMMENT_REGEX = re.compile(r"(?://|#|<!--|/\*|\*).+")

# Разрешенные символы (латиница, пробелы, цифры, знаки препинания)
ENGLISH_REGEX = re.compile(r"^[A-Za-z0-9\s.,!?;:'\"(){}[\]#*/+-]*$")


def get_diff():
    """Получает diff текущего PR с main"""
    try:
        subprocess.run(["git", "fetch", "origin", "main"], check=True)

        result = subprocess.run(
            ["git", "diff", "--unified=0", "origin/main"],
            capture_output=True,
            text=True,
            check=False
        )

        return result.stdout if result.stdout else ""

    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении git diff: {e}")
        return ""


def extract_comments(diff_output):
    """Извлекает комментарии из измененных строк"""
    comments = []
    for line in diff_output.split("\n"):
        if line.startswith("+") and not line.startswith("+++") and COMMENT_REGEX.search(line):
            comments.append(line[1:].strip())  # Убираем "+"
    return comments


def contains_non_english(comment):
    """Проверяет, есть ли в комментарии неанглийские символы"""
    return not ENGLISH_REGEX.match(comment)


def detect_non_english_comments(comments):
    """Фильтрует комментарии с неанглийскими символами"""
    return [comment for comment in comments if contains_non_english(comment)]


def main():
    diff_output = get_diff()
    if not diff_output:
        print("✅ Нет изменений для проверки.")
        return

    comments = extract_comments(diff_output)
    if not comments:
        print("✅ В изменениях нет комментариев.")
        return

    non_english_comments = detect_non_english_comments(comments)
    if non_english_comments:
        print("❌ Найдены комментарии с неанглийскими символами:")
        for comment in non_english_comments:
            print(f"- {comment}")
        exit(1)  # Завершаем GitHub Action с ошибкой

    print("✅ Все комментарии содержат только английские буквы.")


if __name__ == "__main__":
    main()
