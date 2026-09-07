import unittest
from argparse import Namespace
from base64 import b64encode
from contextlib import redirect_stderr
from datetime import datetime
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar
from unittest.mock import patch

from scripts.add_solution import (
    COMMIT_TIMEZONE,
    Completion,
    Kata,
    build_draft,
    collapse_sequential_code_blocks,
    commit_message,
    decode_data_uri,
    drop_leading_heading,
    ensure_folder_is_new,
    extract_images,
    fetch_completion,
    fetch_json,
    filter_conditional_blocks,
    folder_name,
    locate_folder,
    main,
    normalise_title,
    parse_completed_at,
    parse_kata_reference,
    solution_files,
    wait_for_solutions,
    wrap_blocks,
)


class ParseKataReference(unittest.TestCase):
    def test_url_with_train_segment(self):
        url = "https://www.codewars.com/kata/580fe518cefeff16d00000c0/train/sql"
        self.assertEqual(parse_kata_reference(url), "580fe518cefeff16d00000c0")

    def test_url_with_solutions_segment(self):
        url = "https://www.codewars.com/kata/582cba7d3be8ce3a8300007c/solutions/sql"
        self.assertEqual(parse_kata_reference(url), "582cba7d3be8ce3a8300007c")

    def test_slug_url(self):
        url = "https://www.codewars.com/kata/sql-basics-simple-in"
        self.assertEqual(parse_kata_reference(url), "sql-basics-simple-in")

    def test_bare_id(self):
        self.assertEqual(
            parse_kata_reference("580fe518cefeff16d00000c0"), "580fe518cefeff16d00000c0"
        )

    def test_bare_slug_with_surrounding_whitespace(self):
        self.assertEqual(parse_kata_reference(" multiply\n"), "multiply")

    def test_url_without_kata_segment_is_an_error(self):
        with self.assertRaises(SystemExit):
            parse_kata_reference("https://www.codewars.com/users/Sebassu")

    def test_url_ending_in_kata_segment_is_an_error(self):
        with self.assertRaises(SystemExit):
            parse_kata_reference("https://www.codewars.com/kata/")


class Fetching(unittest.TestCase):
    def test_non_json_response_is_an_error(self):
        with (
            patch(
                "scripts.add_solution.fetch_bytes",
                return_value=b"<html>rate limited</html>",
            ),
            self.assertRaises(SystemExit),
        ):
            fetch_json("https://x", "Kata")


class Names(unittest.TestCase):
    def test_title_strips_trailing_space(self):
        self.assertEqual(normalise_title("Find the divisors! "), "Find the divisors!")

    def test_title_strips_trailing_period(self):
        self.assertEqual(
            normalise_title("SQL Basics: Simple table totaling."),
            "SQL Basics: Simple table totaling",
        )

    def test_title_keeps_inner_punctuation(self):
        self.assertEqual(normalise_title("Don't give me five!"), "Don't give me five!")

    def test_title_keeps_an_ellipsis(self):
        self.assertEqual(normalise_title("Wait for it..."), "Wait for it...")

    def test_title_strips_space_before_a_trailing_period(self):
        self.assertEqual(normalise_title("Foo ."), "Foo")

    def test_folder_replaces_slash(self):
        self.assertEqual(
            folder_name("SQL Basics: Simple MIN / MAX"), "SQL Basics: Simple MIN - MAX"
        )


class Completions(unittest.TestCase):
    ENTRIES: ClassVar[list[dict]] = [
        {
            "id": "a",
            "completedAt": "2017-02-10T22:00:07.283Z",
            "completedLanguages": ["cpp", "haskell", "java"],
        },
        {
            "id": "b",
            "completedAt": "2019-11-07T08:17:42.000Z",
            "completedLanguages": ["python"],
        },
        {
            "id": "b",
            "completedAt": "2019-03-02T15:44:18.000Z",
            "completedLanguages": ["python"],
        },
    ]

    def setUp(self):
        response = {"data": self.ENTRIES, "totalPages": 1}
        patcher = patch("scripts.add_solution.fetch_json", return_value=response)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_completed_at_is_converted_to_utc_minus_three(self):
        completed_at = parse_completed_at("2017-02-10T22:00:07.283Z")
        self.assertEqual(
            completed_at,
            datetime(2017, 2, 10, 19, 0, 7, 283000, tzinfo=COMMIT_TIMEZONE),
        )
        self.assertEqual(
            completed_at.isoformat(timespec="seconds"), "2017-02-10T19:00:07-03:00"
        )

    def test_languages_are_collected(self):
        self.assertEqual(
            fetch_completion("Sebassu", "a").languages,
            frozenset({"cpp", "haskell", "java"}),
        )

    def test_earliest_entry_wins_for_duplicate_ids(self):
        completion = fetch_completion("Sebassu", "b")
        self.assertEqual(
            completion.completed_at.isoformat(timespec="seconds"),
            "2019-03-02T12:44:18-03:00",
        )

    def test_missing_kata_is_an_error(self):
        with self.assertRaisesRegex(SystemExit, "not among"):
            fetch_completion("Sebassu", "zzz")


class ConditionalBlocks(unittest.TestCase):
    DESCRIPTION: ClassVar[list[str]] = [
        "Example: (**input --> output**)",
        "~~~if-not:haskell",
        "```",
        '"ATTGC" --> "TAACG"',
        "```",
        "~~~",
        "```if:haskell",
        "dnaStrand [A,T,G,C] `shouldBe` [T,A,C,G]",
        "```",
        "",
    ]

    def test_javascript_keeps_the_if_not_body_unwrapped(self):
        expected = [
            "Example: (**input --> output**)",
            "```",
            '"ATTGC" --> "TAACG"',
            "```",
            "",
        ]
        self.assertEqual(
            filter_conditional_blocks(self.DESCRIPTION, frozenset({"javascript"})),
            expected,
        )

    def test_haskell_keeps_the_if_body(self):
        expected = [
            "Example: (**input --> output**)",
            "dnaStrand [A,T,G,C] `shouldBe` [T,A,C,G]",
            "",
        ]
        self.assertEqual(
            filter_conditional_blocks(self.DESCRIPTION, frozenset({"haskell"})),
            expected,
        )

    def test_two_languages_keep_both_bodies(self):
        result = filter_conditional_blocks(
            self.DESCRIPTION, frozenset({"haskell", "javascript"})
        )
        self.assertIn('"ATTGC" --> "TAACG"', result)
        self.assertIn("dnaStrand [A,T,G,C] `shouldBe` [T,A,C,G]", result)

    def test_comma_list_and_trailing_whitespace_in_info_string(self):
        lines = ["```if:java, csharp   ", "Use `Preloaded`.", "```"]
        self.assertEqual(
            filter_conditional_blocks(lines, frozenset({"csharp"})),
            ["Use `Preloaded`."],
        )
        self.assertEqual(filter_conditional_blocks(lines, frozenset({"sql"})), [])

    def test_four_backtick_opener_keeps_inner_fence(self):
        lines = ["````if:python", "```python", "x = 1", "```", "````"]
        self.assertEqual(
            filter_conditional_blocks(lines, frozenset({"python"})),
            ["```python", "x = 1", "```"],
        )

    def test_plain_fence_body_is_never_interpreted(self):
        lines = ["```", "~~~if:java", "```"]
        self.assertEqual(filter_conditional_blocks(lines, frozenset({"sql"})), lines)

    def test_unterminated_block_runs_to_the_end(self):
        lines = ["intro", "~~~if:sql", "kept", "also kept"]
        self.assertEqual(
            filter_conditional_blocks(lines, frozenset({"sql"})),
            ["intro", "kept", "also kept"],
        )
        self.assertEqual(
            filter_conditional_blocks(lines, frozenset({"java"})), ["intro"]
        )


class SequentialCodeBlocks(unittest.TestCase):
    LINES: ClassVar[list[str]] = [
        "For example:",
        "",
        "```java",
        "isAscOrder(new int[]{1,2}) == true",
        "```",
        "```csharp",
        "IsAscOrder(new int[]{1,2}) == true",
        "```",
        "```haskell",
        "isAscOrder [1,2] == True",
        "```",
        "",
        "Done.",
    ]

    def test_keeps_only_the_completed_language(self):
        expected = [
            "For example:",
            "",
            "```csharp",
            "IsAscOrder(new int[]{1,2}) == true",
            "```",
            "",
            "Done.",
        ]
        self.assertEqual(
            collapse_sequential_code_blocks(self.LINES, frozenset({"csharp"})), expected
        )

    def test_keeps_every_completed_language(self):
        result = collapse_sequential_code_blocks(
            self.LINES, frozenset({"csharp", "haskell"})
        )
        self.assertEqual(result[2:8], self.LINES[5:11])

    def test_falls_back_to_the_first_block(self):
        expected = [
            "For example:",
            "",
            "```java",
            "isAscOrder(new int[]{1,2}) == true",
            "```",
            "",
            "Done.",
        ]
        self.assertEqual(
            collapse_sequential_code_blocks(self.LINES, frozenset({"sql"})), expected
        )

    def test_lone_block_is_untouched(self):
        lines = ["```java", "x", "```"]
        self.assertEqual(
            collapse_sequential_code_blocks(lines, frozenset({"sql"})), lines
        )

    def test_blank_line_separates_groups(self):
        lines = ["```java", "x", "```", "", "```csharp", "y", "```"]
        self.assertEqual(
            collapse_sequential_code_blocks(lines, frozenset({"csharp"})), lines
        )

    def test_untagged_fence_body_is_not_scanned(self):
        lines = ["```", "```java", "```", "```csharp", "y", "```"]
        self.assertEqual(
            collapse_sequential_code_blocks(lines, frozenset({"csharp"})), lines
        )


class LeadingHeading(unittest.TestCase):
    def test_atx_heading_equal_to_title_is_dropped(self):
        lines = ["# Are the numbers in order?", "", "Body"]
        self.assertEqual(
            drop_leading_heading(lines, "Are the numbers in order?"), ["", "Body"]
        )

    def test_comparison_ignores_case_and_leading_blank_lines(self):
        lines = ["", "# Build Tower", "", "Body"]
        self.assertEqual(drop_leading_heading(lines, "Build tower"), ["", "Body"])

    def test_setext_heading_is_dropped(self):
        lines = ["Build Tower", "---", "", "Body"]
        self.assertEqual(drop_leading_heading(lines, "Build Tower"), ["", "Body"])

    def test_heading_with_a_trailing_period_matches_the_title(self):
        lines = ["# SQL Basics: Simple table totaling.", "", "Body"]
        self.assertEqual(
            drop_leading_heading(lines, "SQL Basics: Simple table totaling"),
            ["", "Body"],
        )

    def test_different_heading_is_demoted_to_bold(self):
        lines = ["# The museum of incredibly dull things", "", "Body"]
        expected = ["**The museum of incredibly dull things**", "", "Body"]
        self.assertEqual(drop_leading_heading(lines, "Remove the minimum"), expected)

    def test_lower_level_heading_is_left_alone(self):
        lines = ["#### Once upon a time", "", "Body"]
        self.assertEqual(drop_leading_heading(lines, "Directions Reduction"), lines)

    def test_description_without_heading_is_left_alone(self):
        lines = ["Body", "", "More"]
        self.assertEqual(drop_leading_heading(lines, "Title"), lines)


PNG_BYTES = b"\x89PNG fake"
PNG_DATA_URI = "data:image/png;base64," + b64encode(PNG_BYTES).decode()


class Images(unittest.TestCase):
    def setUp(self):
        self.fetched: list[str] = []
        patcher = patch("scripts.add_solution.fetch_bytes", side_effect=self.fetch)
        patcher.start()
        self.addCleanup(patcher.stop)

    def fetch(self, url: str) -> bytes:
        self.fetched.append(url)
        return f"bytes of {url}".encode()

    def test_base64_data_uri_becomes_diagram_png(self):
        text, images = extract_images(f"![table schema]({PNG_DATA_URI})")
        self.assertEqual(text, "![table schema](./diagram.png)")
        self.assertEqual(images, {"diagram.png": PNG_BYTES})
        self.assertEqual(self.fetched, [])

    def test_protocol_relative_img_tag_is_downloaded(self):
        text, images = extract_images(
            '### Tables:\n<img src="//i.imgur.com/kBkwsbi.png" />'
        )
        self.assertEqual(text, "### Tables:\n![Diagram](./diagram.png)")
        self.assertEqual(self.fetched, ["https://i.imgur.com/kBkwsbi.png"])
        self.assertEqual(
            images["diagram.png"], b"bytes of https://i.imgur.com/kBkwsbi.png"
        )

    def test_img_tag_alt_and_extension_are_kept(self):
        text, images = extract_images('<img alt="Grid" src="http://host/grid.gif">')
        self.assertEqual(text, "![Grid](./diagram.gif)")
        self.assertEqual(list(images), ["diagram.gif"])

    def test_repeated_source_reuses_the_file(self):
        text, images = extract_images(
            '<img src="//h/a.png"> <img src="//h/b.png"> <img src="//h/a.png">'
        )
        self.assertEqual(
            text,
            "![Diagram](./diagram.png) ![Diagram](./diagram-2.png) ![Diagram](./diagram.png)",
        )
        self.assertEqual(list(images), ["diagram.png", "diagram-2.png"])
        self.assertEqual(len(self.fetched), 2)

    def test_reference_style_definition_is_resolved_and_removed(self):
        text, images = extract_images(
            f"See ![schema][tables]\n\n[tables]: {PNG_DATA_URI}\n"
        )
        self.assertEqual(text, "See ![schema](./diagram.png)\n\n")
        self.assertEqual(images, {"diagram.png": PNG_BYTES})

    def test_link_definitions_that_are_not_images_are_kept(self):
        text, images = extract_images("See [docs][1].\n\n[1]: https://example.com\n")
        self.assertEqual(text, "See [docs][1].\n\n[1]: https://example.com\n")
        self.assertEqual(images, {})

    def test_relative_source_is_left_alone(self):
        text, images = extract_images("![x](./local.png)")
        self.assertEqual((text, images), ("![x](./local.png)", {}))

    def test_utf8_svg_data_uri(self):
        text, images = extract_images(
            "![v](data:image/svg+xml;utf8,%3Csvg%3E%3C/svg%3E)"
        )
        self.assertEqual(text, "![v](./diagram.svg)")
        self.assertEqual(images, {"diagram.svg": b"<svg></svg>"})

    def test_unsupported_media_type_is_an_error(self):
        with self.assertRaises(SystemExit):
            extract_images("![x](data:image/webp;base64,AAAA)")

    def test_url_without_extension_is_an_error(self):
        with self.assertRaises(SystemExit):
            extract_images('<img src="https://host/image">')

    def test_reference_with_relative_definition_is_left_alone(self):
        text, images = extract_images(
            "See ![schema][tables]\n\n[tables]: ./local.png\n"
        )
        self.assertEqual(text, "See ![schema][tables]\n\n[tables]: ./local.png\n")
        self.assertEqual(images, {})

    def test_inline_image_is_not_rematched_as_a_reference(self):
        text, images = extract_images(
            "![tables](https://h/y.png)\n\n[tables]: https://h/x.png\n"
        )
        self.assertEqual(
            text, "![tables](./diagram.png)\n\n[tables]: https://h/x.png\n"
        )
        self.assertEqual(len(images), 1)
        self.assertEqual(self.fetched, ["https://h/y.png"])

    def test_data_src_attribute_is_not_mistaken_for_src(self):
        extract_images('<img data-src="https://h/lazy.png" src="https://h/real.png">')
        self.assertEqual(self.fetched, ["https://h/real.png"])

    def test_inline_svg_markup_is_left_alone(self):
        text, images = extract_images("<svg><rect/></svg>")
        self.assertEqual((text, images), ("<svg><rect/></svg>", {}))

    def test_malformed_base64_is_an_error(self):
        with self.assertRaises(SystemExit):
            decode_data_uri("data:image/png;base64,@@@not-base64@@@")


class Wrapping(unittest.TestCase):
    def test_paragraph_is_wrapped_at_88_columns(self):
        words = " ".join(["word"] * 40)
        result = wrap_blocks([words])
        self.assertTrue(all(len(line) <= 88 for line in result.splitlines()))
        self.assertGreater(len(result.splitlines()), 1)
        self.assertEqual(result.replace("\n", " "), words)

    def test_consecutive_lines_are_joined_before_wrapping(self):
        self.assertEqual(
            wrap_blocks(["short line one", "short line two"]),
            "short line one short line two",
        )

    def test_hard_break_ends_the_paragraph(self):
        lines = ["Input strings will only contain letters.  ", "Note: keep the order."]
        self.assertEqual(
            wrap_blocks(lines),
            "Input strings will only contain letters.\n\nNote: keep the order.",
        )

    def test_fenced_code_passes_through_with_trailing_whitespace_stripped(self):
        lines = ["intro", "```", "x = 1   ", "", "y = 2", "```", "outro"]
        self.assertEqual(
            wrap_blocks(lines), "intro\n\n```\nx = 1\n\ny = 2\n```\n\noutro"
        )

    def test_heading_is_split_from_the_following_line(self):
        lines = ["### Tables and relationship below:", "![Diagram](./diagram.png)"]
        self.assertEqual(
            wrap_blocks(lines),
            "### Tables and relationship below:\n\n![Diagram](./diagram.png)",
        )

    def test_list_items_pass_through_unwrapped(self):
        item = "- department (type: text) {group by} [In a real world situation it is bad practice to name a column after a table]"
        self.assertEqual(
            wrap_blocks([item, "- sale_count (type: int)"]),
            f"{item}\n- sale_count (type: int)",
        )

    def test_malformed_heading_is_a_paragraph(self):
        self.assertEqual(
            wrap_blocks(["##Note", "The data is loaded."]), "##Note The data is loaded."
        )

    def test_setext_heading_passes_through(self):
        self.assertEqual(wrap_blocks(["Title", "---"]), "Title\n---")

    def test_table_passes_through(self):
        lines = ["| a | b |", "|---|---|", "| 1 | 2 |"]
        self.assertEqual(wrap_blocks(lines), "\n".join(lines))

    def test_html_block_passes_through(self):
        lines = ["<p>", "text", "</p>"]
        self.assertEqual(wrap_blocks(lines), "\n".join(lines))

    def test_indented_code_passes_through(self):
        self.assertEqual(
            wrap_blocks(["    code line", "    more"]), "    code line\n    more"
        )

    def test_blank_lines_collapse_to_one(self):
        self.assertEqual(wrap_blocks(["a", "", "", "", "b"]), "a\n\nb")

    def test_long_url_is_not_broken(self):
        url = "https://example.com/" + "a" * 100
        result = wrap_blocks([f"See {url} for details about this topic and more."])
        self.assertIn(url, result.splitlines())

    def test_hard_break_does_not_split_a_table(self):
        lines = ["| a | b |  ", "|---|---|", "| 1 | 2 |"]
        self.assertEqual(wrap_blocks(lines), "| a | b |\n|---|---|\n| 1 | 2 |")

    def test_hard_break_does_not_split_a_list(self):
        self.assertEqual(
            wrap_blocks(["- item one  ", "- item two"]), "- item one\n- item two"
        )


class BuildDraft(unittest.TestCase):
    DESCRIPTION = (
        "For this challenge you need to create a simple SELECT statement. Your task is to calculate the MIN,"
        " MEDIAN and MAX scores of the students from the results table.\n\n\n### Tables and relationship below:\n"
        f"![table schema]({PNG_DATA_URI})\n\n### Resultant table:\n- min\n- median\n- max"
    )
    KATA = Kata(
        "58167fa1f544130dcf000317",
        "SQL Statistics: MIN, MEDIAN, MAX",
        "https://www.codewars.com/kata/58167fa1f544130dcf000317",
        DESCRIPTION,
    )
    COMPLETION = Completion(
        datetime(2017, 2, 14, 23, 20, 53, tzinfo=COMMIT_TIMEZONE), frozenset({"sql"})
    )

    def test_readme_and_images(self):
        readme, images = build_draft(self.KATA, self.COMPLETION)
        expected = (
            "# [SQL Statistics: MIN, MEDIAN, MAX](https://www.codewars.com/kata/58167fa1f544130dcf000317)\n\n"
            "For this challenge you need to create a simple SELECT statement. Your task is to\n"
            "calculate the MIN, MEDIAN and MAX scores of the students from the results table.\n\n"
            "### Tables and relationship below:\n\n"
            "![table schema](./diagram.png)\n\n"
            "### Resultant table:\n\n"
            "- min\n- median\n- max\n"
        )
        self.assertEqual(readme, expected)
        self.assertEqual(images, {"diagram.png": PNG_BYTES})

    def test_conditional_blocks_use_the_completed_languages(self):
        kata = Kata(
            "x",
            "T",
            "https://www.codewars.com/kata/x",
            "Intro\n\n~~~if:haskell\nH\n~~~\n\n~~~if-not:haskell\nJ\n~~~\n",
        )
        completion = Completion(self.COMPLETION.completed_at, frozenset({"javascript"}))
        readme, _ = build_draft(kata, completion)
        self.assertEqual(
            readme, "# [T](https://www.codewars.com/kata/x)\n\nIntro\n\nJ\n"
        )

    def test_empty_description_yields_only_the_heading(self):
        kata = Kata("x", "T", "https://www.codewars.com/kata/x", "")
        readme, images = build_draft(kata, self.COMPLETION)
        self.assertEqual(readme, "# [T](https://www.codewars.com/kata/x)\n")
        self.assertEqual(images, {})


class CommitMessage(unittest.TestCase):
    def test_singular(self):
        self.assertEqual(
            commit_message("Multiply", 1), 'Add solution for the "Multiply" problem'
        )

    def test_plural(self):
        self.assertEqual(
            commit_message("Multiply", 3), 'Add solutions for the "Multiply" problem'
        )


class FolderInspection(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.solutions = Path(self.directory.name)
        self.folder = self.solutions / "Directions Reduction"
        self.folder.mkdir()
        (self.folder / "README.md").write_text(
            "# [Directions Reduction](https://www.codewars.com/kata/abc)\n\nBody\n"
        )
        (self.folder / "diagram.png").write_bytes(b"png")
        (self.solutions / "Other").mkdir()
        (self.solutions / "Other" / "README.md").write_text("# Other\n")
        (self.solutions / ".DS_Store").write_bytes(b"")

    def tearDown(self):
        self.directory.cleanup()

    def test_solution_files_ignore_written_and_hidden_files(self):
        (self.folder / "Kata.cs").write_text("class Kata {}")
        (self.folder / "fix.hs").write_text("module Fix where")
        (self.folder / ".DS_Store").write_bytes(b"")
        names = [
            path.name
            for path in solution_files(self.folder, {"README.md", "diagram.png"})
        ]
        self.assertEqual(names, ["Kata.cs", "fix.hs"])

    def test_solution_files_is_empty_before_anything_is_added(self):
        self.assertEqual(solution_files(self.folder, {"README.md", "diagram.png"}), [])

    def test_locate_folder_by_readme_link_after_a_rename(self):
        renamed = self.solutions / "Directions reduction (renamed)"
        self.folder.rename(renamed)
        self.assertEqual(
            locate_folder(self.solutions, "https://www.codewars.com/kata/abc"), renamed
        )

    def test_locate_folder_with_several_matches_is_an_error(self):
        duplicate = self.solutions / "Directions Reduction (copy)"
        duplicate.mkdir()
        (duplicate / "README.md").write_text(
            "# [Copy](https://www.codewars.com/kata/abc)\n"
        )
        with self.assertRaisesRegex(SystemExit, "Several folders"):
            locate_folder(self.solutions, "https://www.codewars.com/kata/abc")

    def test_locate_folder_without_a_match_is_an_error(self):
        with self.assertRaises(SystemExit):
            locate_folder(self.solutions, "https://www.codewars.com/kata/nope")

    def test_existing_folder_is_detected_case_insensitively(self):
        with self.assertRaises(SystemExit):
            ensure_folder_is_new(self.solutions / "directions REDUCTION")
        ensure_folder_is_new(self.solutions / "Brand new")


class Pause(unittest.TestCase):
    def test_reprompts_until_a_solution_file_appears(self):
        with TemporaryDirectory() as directory:
            solutions = Path(directory)
            folder = solutions / "T"
            folder.mkdir()
            (folder / "README.md").write_text(
                "# [T](https://www.codewars.com/kata/abc)\n"
            )
            answers = 0

            def answer(prompt):
                nonlocal answers
                answers += 1
                if answers == 1:
                    return ""
                if answers == 2:
                    (folder / "Kata.cs").write_text("class Kata {}")
                    return ""
                raise AssertionError("pause loop did not stop")

            errors = StringIO()
            with (
                patch("builtins.input", side_effect=answer) as prompt,
                redirect_stderr(errors),
            ):
                result = wait_for_solutions(
                    solutions, "https://www.codewars.com/kata/abc", {"README.md"}
                )
            self.assertEqual(result, (folder, [folder / "Kata.cs"]))
            self.assertEqual(prompt.call_count, 2)
            self.assertIn("No solution file found", errors.getvalue())

    def test_main_reports_eof_at_the_pause_as_aborted(self):
        with (
            patch(
                "scripts.add_solution.parse_args",
                return_value=Namespace(kata="x", username="Sebassu"),
            ),
            patch("scripts.add_solution.run", side_effect=EOFError),
            self.assertRaises(SystemExit) as raised,
        ):
            main()
        self.assertEqual(raised.exception.code, "\nAborted.")


if __name__ == "__main__":
    unittest.main()
