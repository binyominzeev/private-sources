"""
Parser for ChatGPT-generated bilingual (Hebrew/English) paragraph output.

Expected format:

    1.

    עברית:
    Hebrew paragraph text here.

    English:
    English paragraph text here.

    2.

    עברית:
    ...
"""

import re


def parse_chatgpt_output(text: str) -> list[dict]:
    """
    Parse ChatGPT bilingual output and return a list of paragraph dicts.

    Each dict has keys: ``number`` (int), ``hebrew`` (str), ``english`` (str).
    Paragraphs that cannot be parsed are silently skipped.
    """
    results = []

    # Split on paragraph-number headers: one or more digits followed by a full
    # stop (period).  We allow optional whitespace before/after the period and
    # a newline (or end-of-string) right after.
    parts = re.split(r'(?m)^\s*(\d+)\.\s*$', text.strip())

    # parts looks like: [preamble, '1', body1, '2', body2, …]
    i = 1
    while i < len(parts) - 1:
        raw_num = parts[i].strip()
        body = parts[i + 1]
        i += 2

        try:
            number = int(raw_num)
        except ValueError:
            continue

        hebrew_match = re.search(
            r'עברית:\s*\n(.*?)(?=\nEnglish:|\Z)',
            body,
            re.DOTALL,
        )
        english_match = re.search(
            r'English:\s*\n(.*?)(?=\n\d+\.|\Z)',
            body,
            re.DOTALL,
        )

        if not (hebrew_match and english_match):
            continue

        results.append({
            'number': number,
            'hebrew': hebrew_match.group(1).strip(),
            'english': english_match.group(1).strip(),
        })

    return results
