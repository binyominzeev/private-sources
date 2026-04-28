"""
Parser for ChatGPT-generated bilingual (Hebrew/English) paragraph output.

Expected format (with explicit paragraph numbers):

    1.

    עברית:
    Hebrew paragraph text here.

    English:
    English paragraph text here.

    2.

    עברית:
    ...

The parser also handles output where ChatGPT omits the leading numbers (e.g.
when it uses an HTML numbered list that is lost on copy-paste).  In that case
the paragraphs are detected by their עברית:/English: block pairs and numbered
sequentially starting from 1.
"""

import re


def _extract_pairs(bodies: list[str], start_number: int = 1) -> list[dict]:
    """Extract hebrew/english pairs from a list of body strings."""
    results = []
    for idx, body in enumerate(bodies, start=start_number):
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
            'number': idx,
            'hebrew': hebrew_match.group(1).strip(),
            'english': english_match.group(1).strip(),
        })
    return results


def parse_chatgpt_output(text: str) -> list[dict]:
    """
    Parse ChatGPT bilingual output and return a list of paragraph dicts.

    Each dict has keys: ``number`` (int), ``hebrew`` (str), ``english`` (str).
    Paragraphs that cannot be parsed are silently skipped.

    First attempts to split on explicit paragraph-number headers (``1.``,
    ``2.``, etc.).  If no numbered paragraphs are found, falls back to
    detecting עברית:/English: block pairs directly and numbers them
    sequentially from 1.
    """
    stripped = text.strip()
    if not stripped:
        return []

    # ── Numbered mode ──────────────────────────────────────────────────────
    # Split on lines that contain only a number followed by a period.
    parts = re.split(r'(?m)^\s*(\d+)\.\s*$', stripped)
    # parts looks like: [preamble, '1', body1, '2', body2, …]
    if len(parts) > 1:
        numbered_results = []
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
            numbered_results.append({
                'number': number,
                'hebrew': hebrew_match.group(1).strip(),
                'english': english_match.group(1).strip(),
            })
        if numbered_results:
            return numbered_results

    # ── Unnumbered fallback ────────────────────────────────────────────────
    # ChatGPT sometimes omits the "1.", "2.", … headers (substituting an HTML
    # numbered list that is lost on copy-paste).  In that case, split the text
    # on the עברית: marker to isolate each paragraph body, then extract the
    # hebrew/english pair from each chunk and assign sequential numbers.
    chunks = re.split(r'(?m)^עברית:', stripped)
    bodies = ['עברית:' + chunk for chunk in chunks[1:]]  # drop preamble
    return _extract_pairs(bodies)
