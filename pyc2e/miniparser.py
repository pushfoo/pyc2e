"""
Not a full CAOS parser, just enough to detect script boundaries

Tokenization is just a regex.

"""
import re
from re import Match
from typing import List, Dict, DefaultDict, Iterator
from collections import namedtuple, defaultdict


SCRP = "scrp"
RSCR = "rscr"
ENDM = "endm"


SCRIPT_OPENERS = {SCRP, RSCR}
SKIP_TRIGGERS = {
    '*': '\n', # handle comments
    '\"': '\"' # handle quotes
}


# This regex doesn't actually check if the quotes are unescaped.
# Instead, it recognizes the following tokens of interest:
# - scrp
# - rscr
# - endm, including at end of file
# - any quote
# - any asterisk
REGEX_BOUNDARY_TOKENS = re.compile(
    r"(scrp\s+)|(rscr\s+)|(endm(((\s+)|\Z)))|\"|\*|(\n)"
)


# Matches a line terminator (\Z) because it is possible to have a well
# formed scrp header that is not closed with an accompanying endm. It
# would be useful to differentiate between these two cases.
SCRP_HEADER_NUMBERS = re.compile(r"\s*(\d+(\s|\Z)+){4}")

EventScriptSpecifier = namedtuple(
    "EventScriptSpecifier", ['family', 'genus', 'species', 'event']
)

ArgEventsDict = Dict[EventScriptSpecifier, List[str]]
EventsDict = DefaultDict[EventScriptSpecifier, List[str]]

MatchIterator = Iterator[Match]

class ScriptsParse:
    """
    Stores data about a parsing result.

    """
    def __init__(
        self,
        body_caos: List[str] = None,
        events: ArgEventsDict = None,
        removal_scripts: List[str] = None
    ):
        self.body_caos: List[str] = body_caos or []

        self.events: EventsDict = defaultdict(list)
        if events:
            self.events.update(events)

        self.removal_scripts: List[str] = removal_scripts or []


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


def parse_event_specifier(scrp_header: str) -> EventScriptSpecifier:
    """

    Parse an event script specifier tuple from a given scrp header

    :param scrp_header: the scrp header, including the scrp command
    :return:
    """
    l = [int(n) for n in scrp_header.split()]
    return EventScriptSpecifier(*l)


def extract_script(start_token: Match, end_token: Match):
    """
    Extract the script from between two token regex matches.

    For example, if the matches were for rscr and endm:

          v---=-- extracted part ----=----v
    "rscr outs \"script body goes in here\" endm"

    The function would return "outs \"script body goes in here\""

    :param src: the source string to extract from
    :param start_token: the start of the script
    :param end_token:
    :return:
    """
    src = start_token.string
    start_index = start_token.end(0)
    end_index = end_token.start(0)
    return src[start_index:end_index].strip()


def parse(src: str) -> ScriptsParse:
    """
    Extract scripts from the passed comment-stripped source.

    algo:
        start_match = None
        skip_until = None

        for every token_match in matches of interest:
            if skip_until is set:
                if skip_until is ":
                    if token is unescaped ":
                        set skip_until to None

                if its a *:
                    set skip_until to "\n"

            elif its in skip_triggers:
                set skip_until to the mapping char

            elif its an rscr or scrp:
                if the start_match flag is set:
                    error
                set start_match flag to token_match

            elif it's endm:
                if start_match not set:
                    error

                if start_match is scrp
                    parse the scrp header
                    add to the list for that specifier

                if start_match is rscr
                    add to tyhe rscr list

        if start_match still open:
            error


    :return: a parse object with scripts demarcated

    """
    parse = ScriptsParse()

    line_number = 0
    to_start_of_line = 0

    start_match = None
    start_match_string = None

    skip_until = None

    # tokenization is just regex
    token_iterator = REGEX_BOUNDARY_TOKENS.finditer(src)

    for raw_match in token_iterator:

        # used instead of trimmed version as newlines get culled by trim
        raw_match_string = raw_match.group(0)

        if raw_match_string == "\n": # so we can report errors
            line_number += 1

        clean_matched_string = raw_match_string.strip()

        if skip_until:
            if skip_until == '\"' and quote_is_unescaped(raw_match):
                skip_until = None
            elif skip_until == "\n" and raw_match_string == "\n":
                skip_until = None

            continue

        elif raw_match_string in SKIP_TRIGGERS:
            skip_until = clean_matched_string
            start_match = raw_match
            continue

        elif clean_matched_string in SCRIPT_OPENERS:
            if start_match:
                raise ValueError(
                    f"Opened a new script while waiting for"
                    f" '{start_match.group(0)}' to be closed "
                )
            start_match = raw_match
            start_match_string = clean_matched_string

            continue

        elif clean_matched_string == ENDM:
            if not start_match:
                raise ValueError(
                    f"Line {line_number}: Attempted to close script"
                    f" when no script was open"
                )

            if start_match_string == SCRP:

                header_match = SCRP_HEADER_NUMBERS.match(src, start_match.end(0))
                if not header_match:
                    raise ValueError(
                        f"Line {line_number}: scrp is not"
                        f" followed by a proper header"
                    )

                header = parse_event_specifier(header_match.group(0).strip())
                stripped_script = extract_script(header_match, raw_match)

                parse.events[header].append(stripped_script)

            elif start_match == RSCR:
                stripped_script = extract_script(start_match, raw_match)
                parse.removal_scripts.append(stripped_script)

            else:
                raise ValueError(
                    f"Line {line_number}: Impossible condition, '{raw_match_string}'"
                    f" was not an expected value."
                )

            start_match = None
            start_match_string = None

        else:
            raise ValueError(f"Line {line_number}: Unhandled token '{raw_match_string}'")

    return parse
