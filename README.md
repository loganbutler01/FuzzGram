# fuzzgram

Generates random, valid inputs from a grammar and prints them one per line.
Use it to feed test inputs to a program that expects structured input.

From *The Fuzzing Book*, "Fuzzing with Grammars": inputs built from a grammar
are valid by construction, so they get past a program's input checks instead of
being rejected. This is the book's simple grammar fuzzer as a command line tool.

## Usage

You can run the program in one of these 3 ways.

```
uv run synfuzz url
uv run synfuzz expr -n 5 -s 42
uv run synfuzz mygrammar.json -n 100
```

The first argument is the grammar: a built-in name or a path to a JSON file.
With no other options, it prints 10 inputs.

| Option | Meaning |
|---|---|
| `-n`, `--count` | How many inputs to print (default 10) |
| `-s`, `--seed` | Fix the random seed so a run can be repeated |
| `-m`, `--max-nonterminals` | Max unexpanded symbols at once (default 10). Raise it if expansion fails |
| `--check` | Validate the grammar and exit |

## Output

```
# seed: 1
ftp://fuzzingbook.com?def=def&x68=def
https://user:password@cispa.saarland:8080/abc?def=18&x50=x09
https://user:password@fuzzingbook.com:5/x78
```

## Built-in grammars

| Name | Generates |
|---|---|
| `url` | URLs with scheme, host, port, userinfo, path, query |
| `cgi` | URL-encoded strings, like `%0d` and `+` |
| `expr` | Arithmetic expressions, like `-94 / 9` (can get long) |

## Your own grammar

A grammar is a JSON file. Each key is a `<symbol>`, and its value is a list of
the ways it can be written. Generation starts at `<start>`.

```json
{
  "<start>": ["<greeting> <name>"],
  "<greeting>": ["hi", "hello", "yo"],
  "<name>": ["Ada", "Alan", "<name><name>"]
}
```

```
uv run synfuzz greet.json --check
uv run synfuzz greet.json -n 3
```

- `<start>` is required, and every symbol you use must have a rule.
- A symbol can refer to itself (like `<name>` above), which is how you get nesting.
- Repeat an option in a list to make it more likely.

If a rule is wrong, `--check` says which one:

```
synfuzz: invalid grammar:
  <start>: uses undefined <x>
```

## Feeding a program

```
uv run synfuzz url -n 100 | while read -r line; do ./my_program "$line"; done
```
