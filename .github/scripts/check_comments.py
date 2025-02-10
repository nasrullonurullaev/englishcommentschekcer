import os
import re
import subprocess
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent language detection results
DetectorFactory.seed = 0

# File extensions to exclude (localization, config files, etc.)
EXCLUDED_FILES = (".json", ".yaml", ".yml", ".po", ".mo", ".xml")

# Regex to find comments (supports Python, C++, JavaScript, Rust, Go, etc.)
COMMENT_REGEX = re.compile(r"(?://|#|<!--|/\*|\*).+")

def get_diff():
    """Gets the diff of the current PR with the main branch"""
    try:
        # Fetch the latest changes to ensure diff works
        subprocess.run(["git", "fetch", "origin", "main"], check=True)

        # Get diff excluding already existing lines
        result = subprocess.run(
            ["git", "diff", "--unified=0", "origin/main"],
            capture_output=True,
            text=True,
            check=False  # Allow failures but still capture output
        )

        if result.stdout:
            return result.stdout
        else:
            print("⚠️ Warning: git diff returned no output.")
            return ""

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running git diff: {e}")
        return ""

def extract_comments(diff_output):
    """Extracts comments from changed lines"""
    comments = []
    for line in diff_output.split("\n"):
        if line.startswith("+") and not line.startswith("+++") and COMMENT_REGEX.search(line):
            comments.append(line[1:].strip())  # Remove leading "+"
    return comments

def detect_non_english_comments(comments):
    """Detects non-English comments"""
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
        print("✅ No changes to check.")
        return

    comments = extract_comments(diff_output)
    if not comments:
        print("✅ No comments found in changes.")
        return

    non_english_comments = detect_non_english_comments(comments)
    if non_english_comments:
        print("❌ Found non-English comments:")
        for comment, lang in non_english_comments:
            print(f"- {comment} (Detected language: {lang})")
        exit(1)  # Fail the GitHub Action

    print("✅ All comments are in English.")

if __name__ == "__main__":
    main()
