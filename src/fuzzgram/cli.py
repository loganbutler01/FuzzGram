import argparse
import json
import random
import sys

from .core import GRAMMARS, ExpansionError, check, fuzz


def load_grammar(arg):
    if arg in GRAMMARS:
        return GRAMMARS[arg]
    try:
        with open(arg) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"fuzzgram: can't load grammar {arg!r}: {e}")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="fuzzgram",
        description="Generate random valid inputs from a grammar, one per line.",
    )
    p.add_argument("grammar",
                   help=f"built-in ({', '.join(GRAMMARS)}) or path to a JSON grammar file")
    p.add_argument("-n", "--count", type=int, default=10, help="how many inputs (default 10)")
    p.add_argument("-s", "--seed", type=int, help="fix the seed to reproduce a run")
    p.add_argument("-m", "--max-nonterminals", type=int, default=10,
                   help="max unexpanded symbols at once; too low can fail (default 10)")
    p.add_argument("--check", action="store_true", help="validate the grammar and exit")
    args = p.parse_args(argv)

    grammar = load_grammar(args.grammar)
    problems = check(grammar)
    if problems:
        sys.exit("fuzzgram: invalid grammar:\n  " + "\n  ".join(problems))
    if args.check:
        print("grammar ok")
        return

    seed = args.seed if args.seed is not None else random.randrange(2**32)
    print(f"# seed: {seed}", file=sys.stderr)  # stderr so stdout stays pipe-clean
    rng = random.Random(seed)
    try:
        for _ in range(args.count):
            print(fuzz(grammar, rng, args.max_nonterminals))
    except ExpansionError as e:
        sys.exit(f"fuzzgram: {e}")
