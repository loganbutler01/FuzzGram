"""Grammar fuzzing core, following the Fuzzing Book's `simple_grammar_fuzzer`.

A grammar is a dict: nonterminal -> list of alternative expansions.
Nonterminals look like <name>. Generation starts at <start>.
"""
import random
import re

START = "<start>"
RE_NONTERMINAL = re.compile(r"(<[^<> ]*>)")


class ExpansionError(Exception):
    pass


def nonterminals(s):
    return RE_NONTERMINAL.findall(s)


def check(grammar):
    """Return a list of problems. Empty list means the grammar is usable."""
    problems = []
    if START not in grammar:
        problems.append(f"missing {START} rule")
    for symbol, expansions in grammar.items():
        if not isinstance(expansions, list) or not expansions:
            problems.append(f"{symbol}: must be a non-empty list")
            continue
        for exp in expansions:
            if not isinstance(exp, str):
                problems.append(f"{symbol}: {exp!r} is not a string")
                continue
            for used in nonterminals(exp):
                if used not in grammar:
                    problems.append(f"{symbol}: uses undefined {used}")
    return problems


def fuzz(grammar, rng, max_nonterminals=10, max_trials=100):
    """Expand <start> into one string by randomly picking alternatives."""
    term, trials = START, 0
    while nonterminals(term):
        symbol = rng.choice(nonterminals(term))
        new_term = term.replace(symbol, rng.choice(grammar[symbol]), 1)
        if len(nonterminals(new_term)) < max_nonterminals:
            term, trials = new_term, 0
        else:  # expansion grew too much; retry with a different pick
            trials += 1
            if trials >= max_trials:
                raise ExpansionError(f"cannot expand {term!r}; raise -m")
    return term


DIGITS = [str(d) for d in range(10)]

GRAMMARS = {
    "expr": {
        "<start>": ["<expr>"],
        "<expr>": ["<term> + <expr>", "<term> - <expr>", "<term>"],
        "<term>": ["<factor> * <term>", "<factor> / <term>", "<factor>"],
        "<factor>": ["+<factor>", "-<factor>", "(<expr>)",
                     "<integer>.<integer>", "<integer>"],
        "<integer>": ["<digit><integer>", "<digit>"],
        "<digit>": DIGITS,
    },
    "url": {
        "<start>": ["<url>"],
        "<url>": ["<scheme>://<authority><path><query>"],
        "<scheme>": ["http", "https", "ftp", "ftps"],
        "<authority>": ["<host>", "<host>:<port>",
                        "<userinfo>@<host>", "<userinfo>@<host>:<port>"],
        "<host>": ["cispa.saarland", "www.google.com", "fuzzingbook.com"],
        "<port>": ["80", "8080", "<nat>"],
        "<nat>": ["<digit>", "<digit><digit>"],
        "<digit>": DIGITS,
        "<userinfo>": ["user:password"],
        "<path>": ["", "/", "/<id>"],
        "<id>": ["abc", "def", "x<digit><digit>"],
        "<query>": ["", "?<params>"],
        "<params>": ["<param>", "<param>&<params>"],
        "<param>": ["<id>=<id>", "<id>=<nat>"],
    },
    "cgi": {
        "<start>": ["<string>"],
        "<string>": ["<letter>", "<letter><string>"],
        "<letter>": ["<plus>", "<percent>", "<other>"],
        "<plus>": ["+"],
        "<percent>": ["%<hexdigit><hexdigit>"],
        "<hexdigit>": list("0123456789abcdef"),
        "<other>": list("012345abcde-_"),
    },
}
