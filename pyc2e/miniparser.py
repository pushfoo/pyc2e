"""
Not a full CAOS parser, just enough to detect script boundaries for injection.

Uses regex and hacks, leaves real caos parsing to other libraries.

"""
import re
from re import Match
from typing import IO, List, Dict
from collections import namedtuple


SCRP = "scrp"
RSCR = "rscr"
ENDM = "endm"

SCRIPT_OPENERS = {SCRP, RSCR}


# This regex doesn't actually check if the quotes are unescaped. For now,
# a helper function is used to do that because this regex is already ugly
# enough without having nested backwards matching.
TEMPLATE_SCRIPT_DEMARCATION_TOKENS = r"(((scrp(\s+\d+){4})\s+|endm|rscr\s+))|\""
REGEX_BOUNDARY_TOKENS = re.compile(TEMPLATE_SCRIPT_DEMARCATION_TOKENS)


EventScriptSpecifier = namedtuple(
    "EventScriptSpecifier", ['family', 'genus', 'species', 'event']
)
EventsDict = Dict[EventScriptSpecifier, str]


class ScriptsParse:
    """
    Stores data about a parsing result.

    """
    def __init__(
        self,
        body_caos: List[str] = None,
        events: EventsDict = None,
        removal_scripts: List[str] = None
    ):
        self.body_caos: List[str] = body_caos or []
        self.events: EventsDict = events or {}
        self.removal_scripts: List[str] = removal_scripts or []


def read_and_strip_comments(source_stream: IO[str]) -> str:
    """

    Return a version of the source without any comments in it.

    This makes it easier to parse.

    :param source_stream:
    :return:
    """
    lines = []
    for line in source_stream.readlines():
        lines.append(line.split("*", 1)[0])

    return "".join(lines)


def quote_is_unescaped(match: Match) -> bool:
    """
    Returns true if the quote match object is for an unescaped quote.

    This helper will exist until backward matching is fixed in the regex.

    :param match: a regex match object for a quote.
    :return: whether it's unescaped
    """
    quote_index = match.start(0)

    if quote_index  < 2:
        return True

    string = match.string

    if string[quote_index - 1] == "\\" :
        return string[quote_index - 2] != "\\"

    return True


def extract_bounds_from_stripped(stripped_src: str) -> ScriptsParse:
    """
    Extract scripts from the passed comment-stripped source.

    :return: a parse object with scripts demarcated

    """
    parse = ScriptsParse()

    current_start_match = None
    between_quotes = False

    for raw_match in REGEX_BOUNDARY_TOKENS.finditer(stripped_src):

        matched_string = raw_match.group(0).strip()

        if matched_string == "\"":
            if quote_is_unescaped(raw_match):
                between_quotes = not between_quotes

        elif not between_quotes:  # skip any token-like item between quotes
            chars = matched_string[0:4]

            if chars in SCRIPT_OPENERS:  # first 4 chars are an opener
                if current_start_match:
                    raise ValueError(
                        f"Opened a new script while waiting for '{current_start_match.group(0)}' to be closed")

                current_start_match = raw_match

            else:  # it has to be an endm, close & store current context
                snippet = stripped_src[current_start_match.end(0):raw_match.start(0)].strip()

                if chars == SCRP:
                    specifier = EventScriptSpecifier(*[int(n) for n in matched_string[4:].split()])
                    parse.events.update({specifier : snippet})

                else:
                    parse.removal_scripts.append(snippet)

    return parse
