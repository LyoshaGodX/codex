import json
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
CONFIG_PATH = os.path.join(BASE_DIR, "updated.json")


CARD_DOT = '<span class="update-dot"></span>'
CARD_TOOLTIP = '<span class="dot-tooltip">Недавно добавлено</span>'

ARTICLE_BADGE = '<span class="badge-updated">Недавно добавлено</span>'


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data)


def process_index(updated_keys):
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'\n[ \t]*<span class="update-dot"></span>', "", html)
    html = re.sub(r'\n[ \t]*<span class="dot-tooltip">[^<]*</span>', "", html)
    html = html.replace('class="card card-updated"', 'class="card"')

    for key in updated_keys:
        filename = f"articles/{key}.html"
        old = f'<a href="{filename}" class="card">'
        if old not in html:
            print(f"  [!] Карточка для {key} не найдена в index.html")
            continue

        new_card_tag = f'<a href="{filename}" class="card card-updated">'
        replacement = (
            f'{new_card_tag}\n'
            f'        {CARD_DOT}\n'
            f'        {CARD_TOOLTIP}'
        )
        html = html.replace(old, replacement)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("  index.html обновлён")


def process_article(key, should_mark):
    path = os.path.join(ARTICLES_DIR, f"{key}.html")
    if not os.path.exists(path):
        print(f"  [!] Файл {key}.html не найден")
        return

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    has_badge = "badge-updated" in html

    if should_mark and not has_badge:
        html = re.sub(
            r'(</h1>)\s*(\n\s*</div>)',
            rf'\1\n        {ARTICLE_BADGE}\2',
            html,
            count=1,
        )
        print(f"  + {key}.html — бейдж добавлен")

    elif not should_mark and has_badge:
        html = re.sub(r'\s*<span class="badge-updated">.*?</span>', "", html)
        print(f"  − {key}.html — бейдж удалён")

    else:
        action = "уже есть" if has_badge else "не требуется"
        print(f"  ~ {key}.html — {action}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    updated_keys = load_config()

    all_keys = set()
    for fname in os.listdir(ARTICLES_DIR):
        if fname.endswith(".html"):
            all_keys.add(fname[:-5])

    process_index(updated_keys)

    for key in sorted(all_keys):
        process_article(key, key in updated_keys)



if __name__ == "__main__":
    main()
