"""Vietnamese text normalization and controlled query augmentation."""

from __future__ import annotations

import random
import re
import unicodedata


TEEN_CODE_REPLACEMENTS = {
    "không": ["ko", "khong", "k"],
    "được": ["dc", "đc"],
    "bác sĩ": ["bs", "bac si"],
    "dược sĩ": ["ds", "duoc si"],
    "thuốc": ["thuoc"],
    "uống": ["uong"],
    "liều": ["lieu"],
    "huyết áp": ["ha", "huyet ap"],
    "tiểu đường": ["td", "tieu duong"],
    "kháng sinh": ["ks", "khang sinh"],
    "paracetamol": ["para", "paracetamol"],
    "ibuprofen": ["ibu", "ibuprofen"],
}


PREFIX_VARIANTS = [
    "",
    "Cho em hỏi, ",
    "Mình hỏi chút, ",
    "Ba em đang bị vậy: ",
    "Mẹ em hỏi giúp: ",
]


def normalize_vi_text(text: str) -> str:
    """Normalize Vietnamese text without removing meaning-bearing accents."""

    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.?!:;])", r"\1", text)
    return text


def remove_vietnamese_accents(text: str) -> str:
    """Create a no-accent variant for robustness to informal typing."""

    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")


def make_informal_variants(question: str, max_variants: int = 4, seed: int = 42) -> list[str]:
    """Create realistic Vietnamese variants: no accents, abbreviations, prefixes."""

    rng = random.Random(f"{seed}:{question}")
    base = normalize_vi_text(question)
    variants = {base}
    variants.add(remove_vietnamese_accents(base))

    lowered = base
    for formal, informal_options in TEEN_CODE_REPLACEMENTS.items():
        if formal in lowered.lower():
            for informal in informal_options:
                pattern = re.compile(re.escape(formal), re.IGNORECASE)
                variants.add(pattern.sub(informal, base))

    for prefix in rng.sample(PREFIX_VARIANTS, k=min(len(PREFIX_VARIANTS), 3)):
        if prefix:
            variants.add(prefix + base[0].lower() + base[1:])

    clean = [normalize_vi_text(item) for item in variants if item.strip()]
    clean = [item for item in clean if item != base]
    rng.shuffle(clean)
    return clean[:max_variants]

