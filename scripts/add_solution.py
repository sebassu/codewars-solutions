#!/usr/bin/env python3
"""Record a solved CodeWars kata: create its folder with a draft README, wait for the solution files
to be added by hand, then commit the folder dated at the kata's completion time."""

import json
import os
import re
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from operator import itemgetter
from pathlib import Path
from textwrap import fill
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

API_ROOT = "https://www.codewars.com/api/v1"
USER_AGENT = "codewars-solutions/add_solution.py"
CODEWARS_USERNAME = "Sebassu"
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS_DIRECTORY = REPOSITORY_ROOT / "solutions"
WRAP_WIDTH = 88
COMMIT_TIMEZONE = timezone(timedelta(hours=-3))
LANGUAGE_IDS = frozenset(
    {
        "agda",
        "bf",
        "c",
        "cfml",
        "clojure",
        "cobol",
        "coffeescript",
        "commonlisp",
        "coq",
        "cpp",
        "crystal",
        "csharp",
        "d",
        "dart",
        "elixir",
        "elm",
        "erlang",
        "factor",
        "forth",
        "fortran",
        "fsharp",
        "go",
        "groovy",
        "haskell",
        "haxe",
        "idris",
        "java",
        "javascript",
        "julia",
        "kotlin",
        "lambdacalc",
        "lean",
        "lua",
        "nasm",
        "nim",
        "objc",
        "ocaml",
        "pascal",
        "perl",
        "php",
        "powershell",
        "prolog",
        "purescript",
        "python",
        "r",
        "racket",
        "raku",
        "reason",
        "riscv",
        "ruby",
        "rust",
        "scala",
        "shell",
        "solidity",
        "sql",
        "swift",
        "typescript",
        "vb",
    }
)
IMAGE_EXTENSIONS = {
    "image/png": "png",
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "image/svg+xml": "svg",
}

FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CONDITION_PATTERN = re.compile(r"^(if|if-not):(.+)$")
ATX_H1_PATTERN = re.compile(r"^ {0,3}# +(.+?)\s*(?:#+\s*)?$")
ATX_HEADING_PATTERN = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")
SETEXT_UNDERLINE_PATTERN = re.compile(r"^ {0,3}(=+|-+)\s*$")
PASSTHROUGH_PATTERN = re.compile(
    r"^(?: {0,3}(?:[-+*]|\d{1,9}[.)])\s| {0,3}>| {0,3}\||\t| {4}| {0,3}<[A-Za-z/!])"
)
TABLE_DELIMITER_PATTERN = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
DATA_URI_PATTERN = re.compile(r"^data:([^;,]+)((?:;[^;,]+)*),(.*)$", re.DOTALL)
INLINE_IMAGE_PATTERN = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\(\s*(?P<source>[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)"
)
REFERENCE_IMAGE_PATTERN = re.compile(
    r"!\[(?P<alt>[^\]]*)\](?:\[(?P<label>[^\]]*)\])?(?!\()"
)
REFERENCE_DEFINITION_PATTERN = re.compile(
    r"^ {0,3}\[(?P<label>[^\]]+)\]:[ \t]*(?P<source>\S+)[ \t]*\n?", re.MULTILINE
)
HTML_IMAGE_PATTERN = re.compile(r"<img\b[^>]*>", re.IGNORECASE)


@dataclass(frozen=True)
class Kata:
    id: str
    title: str
    url: str
    description: str


@dataclass(frozen=True)
class Completion:
    completed_at: datetime
    languages: frozenset[str]


@dataclass(frozen=True)
class Fence:
    marker: str
    info: str

    def closes(self, opener: "Fence") -> bool:
        return (
            self.marker[0] == opener.marker[0]
            and len(self.marker) >= len(opener.marker)
            and not self.info
        )


def run(kata_reference: str, username: str) -> None:
    kata = fetch_kata(kata_reference)
    completion = fetch_completion(username, kata.id)
    folder = SOLUTIONS_DIRECTORY / folder_name(kata.title)
    ensure_folder_is_new(folder)
    readme, images = build_draft(kata, completion)
    written = write_draft(folder, readme, images)
    print_summary(folder, written, completion)
    folder, solutions = wait_for_solutions(
        SOLUTIONS_DIRECTORY, kata.url, {path.name for path in written}
    )
    commit_folder(folder, solutions, completion)


def fetch_kata(reference: str) -> Kata:
    id_or_slug = parse_kata_reference(reference)
    data = fetch_json(
        f"{API_ROOT}/code-challenges/{id_or_slug}", f"Kata {id_or_slug!r}"
    )
    return Kata(
        data["id"], normalise_title(data["name"]), data["url"], data["description"]
    )


def parse_kata_reference(reference: str) -> str:
    segments = [
        segment for segment in urlparse(reference.strip()).path.split("/") if segment
    ]
    if "kata" in segments and (index := segments.index("kata") + 1) < len(segments):
        return segments[index]
    if len(segments) == 1 and segments[0] != "kata":
        return segments[0]
    sys.exit(f"error: Cannot find a kata id or slug in {reference!r}")


def fetch_json(url: str, subject: str) -> dict:
    try:
        return json.loads(fetch_bytes(url, subject))
    except ValueError:
        sys.exit(f"error: {subject}: unexpected non-JSON response from {url}")


def fetch_bytes(url: str, subject: str | None = None) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=30) as response:
            return response.read()
    except HTTPError as error:
        if error.code == 404 and subject:
            sys.exit(f"error: {subject} not found")
        sys.exit(f"error: Fetching {url} failed: HTTP {error.code}")
    except URLError as error:
        sys.exit(f"error: Fetching {url} failed: {error.reason}")


def normalise_title(name: str) -> str:
    return re.sub(r"(?<!\.)\.$", "", name.strip()).rstrip()


def fetch_completion(username: str, kata_id: str) -> Completion:
    entries: list[dict] = []
    page, total_pages = 0, 1
    while page < total_pages:
        url = (
            f"{API_ROOT}/users/{quote(username)}/code-challenges/completed?page={page}"
        )
        data = fetch_json(url, f"User {username!r}")
        entries.extend(entry for entry in data["data"] if entry["id"] == kata_id)
        total_pages = data["totalPages"]
        page += 1
    if not entries:
        sys.exit(f"error: Kata {kata_id} is not among {username}'s completed katas")
    earliest = min(entries, key=itemgetter("completedAt"))
    return Completion(
        parse_completed_at(earliest["completedAt"]),
        frozenset(earliest["completedLanguages"]),
    )


def parse_completed_at(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(COMMIT_TIMEZONE)


def folder_name(title: str) -> str:
    return title.replace("/", "-")


def ensure_folder_is_new(folder: Path) -> None:
    if folder.name.casefold() in {
        path.name.casefold() for path in folder.parent.iterdir()
    }:
        sys.exit(f"error: {folder} already exists")


def build_draft(kata: Kata, completion: Completion) -> tuple[str, dict[str, bytes]]:
    lines = drop_leading_heading(kata.description.splitlines(), kata.title)
    lines = filter_conditional_blocks(lines, completion.languages)
    lines = collapse_sequential_code_blocks(lines, completion.languages)
    body, images = extract_images("\n".join(lines))
    parts = (f"# [{kata.title}]({kata.url})", wrap_blocks(body.splitlines()))
    return "\n\n".join(part for part in parts if part) + "\n", images


def drop_leading_heading(lines: list[str], title: str) -> list[str]:
    first = next(
        (index for index, line in enumerate(lines) if line.strip()), len(lines)
    )
    rest = lines[first:]
    if not rest:
        return rest
    if match := ATX_H1_PATTERN.match(rest[0]):
        heading, remainder = match[1], rest[1:]
    elif len(rest) > 1 and SETEXT_UNDERLINE_PATTERN.match(rest[1]):
        heading, remainder = rest[0].strip(), rest[2:]
    else:
        return rest
    if normalise_title(heading).casefold() == title.casefold():
        return remainder
    return [f"**{heading}**", *remainder]


def filter_conditional_blocks(
    lines: list[str], completed_languages: frozenset[str]
) -> list[str]:
    result: list[str] = []
    index = 0
    while index < len(lines):
        if (fence := parse_fence(lines[index])) is None:
            result.append(lines[index])
            index += 1
            continue
        end = find_closing_fence(lines, index + 1, fence)
        if (holds := condition_holds(fence.info, completed_languages)) is None:
            result.extend(lines[index : end + 1])
        elif holds:
            result.extend(lines[index + 1 : end])
        index = end + 1
    return result


def parse_fence(line: str) -> Fence | None:
    if (match := FENCE_PATTERN.match(line)) is None:
        return None
    marker, info = match.groups()
    if marker[0] == "`" and "`" in info:
        return None
    return Fence(marker, info.strip())


def condition_holds(info: str, completed_languages: frozenset[str]) -> bool | None:
    if (match := CONDITION_PATTERN.match(info)) is None:
        return None
    keyword, languages = match.groups()
    block_languages = frozenset(language.strip() for language in languages.split(","))
    if keyword == "if":
        return bool(block_languages & completed_languages)
    return bool(completed_languages - block_languages)


def find_closing_fence(lines: list[str], start: int, opener: Fence) -> int:
    for index in range(start, len(lines)):
        if (fence := parse_fence(lines[index])) is not None and fence.closes(opener):
            return index
    return len(lines)


def collapse_sequential_code_blocks(
    lines: list[str], completed_languages: frozenset[str]
) -> list[str]:
    result: list[str] = []
    index = 0
    while index < len(lines):
        run, end = language_block_run(lines, index)
        if len(run) > 1:
            run = [block for block in run if block[0] in completed_languages] or run[:1]
        if run:
            result.extend(line for _, block_lines in run for line in block_lines)
            index = end
        elif (fence := parse_fence(lines[index])) is not None:
            end = find_closing_fence(lines, index + 1, fence)
            result.extend(lines[index : end + 1])
            index = end + 1
        else:
            result.append(lines[index])
            index += 1
    return result


def language_block_run(
    lines: list[str], start: int
) -> tuple[list[tuple[str, list[str]]], int]:
    run: list[tuple[str, list[str]]] = []
    index = start
    while (
        index < len(lines)
        and (fence := parse_fence(lines[index])) is not None
        and fence.info in LANGUAGE_IDS
    ):
        end = find_closing_fence(lines, index + 1, fence)
        run.append((fence.info, lines[index : end + 1]))
        index = end + 1
    return run, index


def extract_images(text: str) -> tuple[str, dict[str, bytes]]:
    definitions = {
        match["label"]: match["source"]
        for match in REFERENCE_DEFINITION_PATTERN.finditer(text)
    }
    used_labels: set[str] = set()
    filenames: dict[str, str] = {}
    images: dict[str, bytes] = {}

    def reference(alt: str, source: str, original: str) -> str:
        if not is_fetchable(source):
            return original
        if source not in filenames:
            content, extension = load_image(source)
            suffix = f"-{len(images) + 1}" if images else ""
            filenames[source] = f"diagram{suffix}.{extension}"
            images[filenames[source]] = content
        return f"![{alt or 'Diagram'}](./{filenames[source]})"

    def reference_by_label(match: re.Match) -> str:
        label = match["label"] or match["alt"]
        if label not in definitions or not is_fetchable(definitions[label]):
            return match[0]
        used_labels.add(label)
        return reference(match["alt"] or label, definitions[label], match[0])

    text = INLINE_IMAGE_PATTERN.sub(
        lambda match: reference(match["alt"], match["source"], match[0]), text
    )
    text = REFERENCE_IMAGE_PATTERN.sub(reference_by_label, text)
    text = REFERENCE_DEFINITION_PATTERN.sub(
        lambda match: "" if match["label"] in used_labels else match[0], text
    )
    text = HTML_IMAGE_PATTERN.sub(
        lambda match: reference(
            html_attribute(match[0], "alt"), html_attribute(match[0], "src"), match[0]
        ),
        text,
    )
    return text, images


def is_fetchable(source: str) -> bool:
    return source.startswith(("data:", "http://", "https://", "//"))


def load_image(source: str) -> tuple[bytes, str]:
    if source.startswith("data:"):
        return decode_data_uri(source)
    url = f"https:{source}" if source.startswith("//") else source
    if not (extension := Path(urlparse(url).path).suffix.lstrip(".").lower()):
        sys.exit(f"error: Cannot tell the image type of {url}")
    return fetch_bytes(url), extension


def decode_data_uri(source: str) -> tuple[bytes, str]:
    if (match := DATA_URI_PATTERN.match(source)) is None:
        sys.exit(f"error: Malformed data URI: {source[:40]}...")
    media_type, parameters, data = match.groups()
    if (extension := IMAGE_EXTENSIONS.get(media_type)) is None:
        sys.exit(f"error: Unsupported image type {media_type}")
    try:
        content = b64decode(data) if ";base64" in parameters else unquote(data).encode()
    except ValueError:
        sys.exit("error: Malformed base64 image data")
    return content, extension


def html_attribute(tag: str, name: str) -> str:
    match = re.search(
        rf"(?<![\w-]){name}\s*=\s*[\"']([^\"']*)[\"']", tag, re.IGNORECASE
    )
    return match[1] if match else ""


def wrap_blocks(lines: list[str]) -> str:
    return "\n\n".join(render_block(block) for block in split_blocks(lines))


def split_blocks(lines: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []

    def close() -> None:
        nonlocal current
        if current:
            blocks.append(current)
            current = []

    index = 0
    while index < len(lines):
        line = lines[index]
        if (fence := parse_fence(line)) is not None:
            close()
            end = find_closing_fence(lines, index + 1, fence)
            blocks.append(lines[index : end + 1])
            index = end + 1
            continue
        if not line.strip():
            close()
        elif ATX_HEADING_PATTERN.match(line):
            close()
            blocks.append([line])
        else:
            current.append(line)
            if line.endswith("  ") and not PASSTHROUGH_PATTERN.match(current[0]):
                close()
        index += 1
    close()
    return blocks


def render_block(block: list[str]) -> str:
    if is_passthrough(block):
        return "\n".join(line.rstrip() for line in block)
    text = " ".join(line.strip() for line in block)
    return fill(text, WRAP_WIDTH, break_long_words=False, break_on_hyphens=False)


def is_passthrough(block: list[str]) -> bool:
    return (
        parse_fence(block[0]) is not None
        or ATX_HEADING_PATTERN.match(block[0]) is not None
        or PASSTHROUGH_PATTERN.match(block[0]) is not None
        or any(SETEXT_UNDERLINE_PATTERN.match(line) for line in block[1:])
        or (len(block) > 1 and TABLE_DELIMITER_PATTERN.match(block[1]) is not None)
    )


def write_draft(folder: Path, readme: str, images: dict[str, bytes]) -> list[Path]:
    folder.mkdir()
    files = {"README.md": readme.encode(), **images}
    for name, content in files.items():
        (folder / name).write_bytes(content)
    return [folder / name for name in files]


def print_summary(folder: Path, written: list[Path], completion: Completion) -> None:
    print(f"Created {folder.relative_to(REPOSITORY_ROOT)}/")
    for path in written:
        print(f"  {path.name}")
    languages = ", ".join(sorted(completion.languages))
    print(
        f"Completed {completion.completed_at.isoformat(' ', 'seconds')} in {languages}"
    )


def wait_for_solutions(
    solutions_directory: Path, kata_url: str, written: set[str]
) -> tuple[Path, list[Path]]:
    prompt = (
        "Add the solution file(s) and edit README.md as needed (keep the heading link), "
        "then press Enter to commit. Ctrl-C leaves the folder uncommitted. "
    )
    while True:
        input(prompt)
        folder = locate_folder(solutions_directory, kata_url)
        if solutions := solution_files(folder, written):
            return folder, solutions
        print(f"No solution file found in {folder.name}/", file=sys.stderr)


def locate_folder(solutions_directory: Path, kata_url: str) -> Path:
    matches = [
        candidate
        for candidate in sorted(solutions_directory.iterdir())
        if (readme := candidate / "README.md").is_file()
        and kata_url in readme.read_text(encoding="utf-8").partition("\n")[0]
    ]
    if len(matches) > 1:
        names = ", ".join(match.name for match in matches)
        sys.exit(f"error: Several folders link to {kata_url}: {names}")
    if not matches:
        sys.exit(
            f"error: No folder under {solutions_directory} has a README linking to {kata_url}"
        )
    return matches[0]


def solution_files(folder: Path, written: set[str]) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.name not in written and not path.name.startswith(".")
    )


def commit_folder(folder: Path, solutions: list[Path], completion: Completion) -> None:
    date = completion.completed_at.isoformat(timespec="seconds")
    message = commit_message(folder.name, len(solutions))
    git("add", "--", str(folder))
    git(
        "commit",
        "--only",
        "--message",
        message,
        f"--date={date}",
        "--",
        str(folder),
        GIT_COMMITTER_DATE=date,
    )


def commit_message(folder_name: str, solution_count: int) -> str:
    noun = "solution" if solution_count == 1 else "solutions"
    return f'Add {noun} for the "{folder_name}" problem'


def git(*arguments: str, **environment: str) -> None:
    subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY_ROOT,
        check=True,
        env={**os.environ, **environment},
    )


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("kata", help="kata URL, id or slug")
    parser.add_argument(
        "--username",
        default=CODEWARS_USERNAME,
        help="CodeWars username (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    try:
        run(arguments.kata, arguments.username)
    except OSError as error:
        sys.exit(f"error: {error}")
    except subprocess.CalledProcessError as error:
        sys.exit(
            f"error: {' '.join(error.cmd)} exited with {error.returncode}; "
            "the folder is left uncommitted"
        )
    except (KeyboardInterrupt, EOFError):
        sys.exit("\nAborted.")


if __name__ == "__main__":
    main()
