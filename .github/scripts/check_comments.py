import os
import re
import subprocess

# File extensions to exclude (localization, config files, etc.)
EXCLUDED_FILES = (".json", ".yaml", ".yml", ".po", ".mo", ".xml")

# Regex to find comments (supports Python, C++, JavaScript, Rust, Go, etc.)
COMMENT_REGEX = re.compile(r"(?://|#|<!--|/\*|\*).+")

# Regex to detect non-English letters (anything that is not a-z, A-Z, 0-9, punctuation, or spaces)
NON_ENGLISH_REGEX = re.compile(r"[^\x00-\x7F]")  # Matches any non-ASCII character

def get_base_branch():
    """Gets the base branch of the current PR from GitHub Actions environment"""
    return os.getenv("GITHUB_BASE_REF", "main")  # Default to 'main' if not in CI

def get_diff():
    """Gets the diff of the current PR with the base branch"""
    base_branch = get_base_branch()
    print(f"🔍 Checking diff against: {base_branch}")

    try:
        subprocess.run(["git", "fetch", "origin", base_branch], check=True)

        result = subprocess.run(
            ["git", "diff", "--unified=0", f"origin/{base_branch}"],
            capture_output=True,
            text=True,
            check=False  # Allow failures but still capture output
        )

        return result.stdout if result.stdout else ""

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running git diff: {e}")
        return ""

def extract_comments(diff_output):
    """Extracts comments from changed lines"""
    comments = []
    for line in diff_output.split("\n"):
        if line.startswith("+") and not line.startswith("+++") and COMMENT_REGEX.search(line):
            comments.append(line[1:].strip())  # Remove "+"
    return comments

def contains_non_english(text):
    """Checks if a string contains non-English characters"""
    return bool(NON_ENGLISH_REGEX.search(text))

def detect_non_english_comments(comments):
    """Filters comments that contain non-English characters"""
    non_english = [comment for comment in comments if contains_non_english(comment)]
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
        print("❌ Found comments with non-English characters:")
        for comment in non_english_comments:
            print(f"- {comment}")
        exit(1)  # Fail the GitHub Action

    print("✅ All comments contain only English letters.")

if __name__ == "__main__":
    main()
