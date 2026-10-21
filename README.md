# fuzzgram

Tiny grammar-based fuzzer. Based on "Fuzzing with Grammars" (The Fuzzing Book).

```
uv run fuzzgram url -n 5
```

Custom grammar (JSON): `{"<start>": ["<greeting>"], "<greeting>": ["hi", "hello"]}`
Then: `fuzzgram my_grammar.json --check` and `fuzzgram my_grammar.json -n 20`
