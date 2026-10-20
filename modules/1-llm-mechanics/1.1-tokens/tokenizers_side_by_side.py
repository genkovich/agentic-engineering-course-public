"""Same text through three open tokenizers, side by side.

cl100k (GPT-4) and o200k (GPT-4o, GPT-5) come from tiktoken, Gemma 3 from
Hugging Face tokenizers. Every token gets its own background colour, so you
see where each tokenizer cuts. No API key needed.

Usage: python3 tokenizers_side_by_side.py ["your text"]
"""
import os
import sys

import tiktoken
from huggingface_hub import hf_hub_download
from huggingface_hub.errors import LocalEntryNotFoundError
from huggingface_hub.utils import logging as hf_logging
from tokenizers import Tokenizer

DEFAULT_TEXT = "Токенізація"

# Not gated on Hugging Face, so no HF token or license click is needed.
GEMMA_REPO = "unsloth/gemma-3-1b-it"

# Background colours for neighbouring tokens (ANSI 256-colour palette).
BACKGROUNDS = [217, 153, 186, 151, 223, 183]

USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def tiktoken_pieces(encoding_name: str, text: str) -> list[str]:
    enc = tiktoken.get_encoding(encoding_name)
    # A token can hold half of a Cyrillic letter (UTF-8 is 2 bytes per letter),
    # such a piece decodes to "�".
    return [
        enc.decode_single_token_bytes(t).decode("utf-8", errors="replace")
        for t in enc.encode(text)
    ]


def gemma_tokenizer_path() -> str:
    # Cache first: after the first download the script works offline and
    # the Hub does not print its "unauthenticated requests" warning.
    try:
        return hf_hub_download(GEMMA_REPO, "tokenizer.json", local_files_only=True)
    except LocalEntryNotFoundError:
        hf_logging.set_verbosity_error()
        return hf_hub_download(GEMMA_REPO, "tokenizer.json")


def gemma_pieces(text: str) -> list[str]:
    tok = Tokenizer.from_file(gemma_tokenizer_path())
    enc = tok.encode(text, add_special_tokens=False)
    return [text[start:end] for start, end in enc.offsets]


def render(pieces: list[str]) -> str:
    out = []
    for i, piece in enumerate(pieces):
        piece = piece.replace("\n", "⏎")
        if USE_COLOR:
            bg = BACKGROUNDS[i % len(BACKGROUNDS)]
            out.append(f"\033[48;5;{bg}m\033[38;5;16m{piece}\033[0m")
        else:
            out.append(piece)
    # Without colours (pipe, NO_COLOR) the boundaries are shown with "|".
    return "".join(out) if USE_COLOR else "|".join(out)


def main() -> None:
    text = " ".join(sys.argv[1:]) or DEFAULT_TEXT

    rows = [
        ("cl100k (GPT-4)", tiktoken_pieces("cl100k_base", text)),
        ("o200k (GPT-4o)", tiktoken_pieces("o200k_base", text)),
        ("Gemma 3", gemma_pieces(text)),
    ]

    print(f"Текст: {text}  (символів: {len(text)})\n")
    width = max(len(name) for name, _ in rows)
    for name, pieces in rows:
        print(f"  {name:<{width}}  {len(pieces):>3} ток.   {render(pieces)}")

    if any("�" in p for _, pieces in rows for p in pieces):
        print("\n  � = токен розрізав літеру посередині: кирилична літера займає 2 байти")


if __name__ == "__main__":
    main()
