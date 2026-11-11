"""Cost calculator for lesson 1.2.

Same scenario as the lesson 1.2 homework: an agent with a 5,000-token system
prompt gets a 300-token user request, thinks for 2,000 tokens and answers with
800 tokens. How much do 1,000 such requests cost:

  1. without caching,
  2. with the system prompt cached,
  3. with caching AND the Batch API.

No API key needed: it is plain arithmetic. Do the homework by hand first,
then run this to check your numbers.

Prices are per 1M tokens. Pass your own with --input/--output/--cache-read/
--cache-write/--batch-discount if you use a different model or the prices on
the "Актуальний стан" page differ.
"""
import argparse

# Claude API prices per 1M tokens, checked on 2026-11-11 at
# https://platform.claude.com/docs/en/about-claude/pricing
# cache_write = 5-minute cache write. Batch API = 50% off everything.
# Haiku 5.5 prices are for prompts up to 100K tokens.
PRICES_DATE = "2026-11-11"
MODELS = {
    "claude-opus-5-5":   {"input": 4.00, "output": 20.00, "cache_write": 5.00,  "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_write": 2.50,  "cache_read": 0.10},
    "claude-haiku-5-5":  {"input": 0.10, "output": 0.50,  "cache_write": 0.125, "cache_read": 0.01},
}
BATCH_DISCOUNT = 0.5

MTOK = 1_000_000


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="claude-sonnet-5-5", choices=sorted(MODELS))
    p.add_argument("--system", type=int, default=5_000, help="system prompt tokens")
    p.add_argument("--user", type=int, default=300, help="user request tokens")
    p.add_argument("--thinking", type=int, default=2_000, help="thinking tokens (billed as output)")
    p.add_argument("--answer", type=int, default=800, help="answer tokens")
    p.add_argument("--requests", type=int, default=1_000)
    p.add_argument("--input", type=float, help="override: input $/1M")
    p.add_argument("--output", type=float, help="override: output $/1M")
    p.add_argument("--cache-write", type=float, help="override: cache write $/1M")
    p.add_argument("--cache-read", type=float, help="override: cache read $/1M")
    p.add_argument("--batch-discount", type=float, default=BATCH_DISCOUNT,
                   help="share of the price you DON'T pay with Batch API (0.5 = 50%% off; 0 = no batch)")
    return p.parse_args()


def usd(x: float) -> str:
    return f"${x:,.4f}"


def main() -> None:
    a = parse_args()
    price = dict(MODELS[a.model])
    for key, val in (("input", a.input), ("output", a.output),
                     ("cache_write", a.cache_write), ("cache_read", a.cache_read)):
        if val is not None:
            price[key] = val

    n = a.requests
    input_tok = a.system + a.user
    output_tok = a.thinking + a.answer  # thinking is already output, don't add it twice

    print(f"Model: {a.model}   prices per 1M tokens as of {PRICES_DATE}")
    print(f"  input {usd(price['input'])}  output {usd(price['output'])}  "
          f"cache write {usd(price['cache_write'])}  cache read {usd(price['cache_read'])}")
    print(f"Scenario: {n} requests x ({a.system} system + {a.user} user) input, "
          f"({a.thinking} thinking + {a.answer} answer) output\n")

    # 1. No cache
    in1 = n * input_tok / MTOK * price["input"]
    out = n * output_tok / MTOK * price["output"]
    total1 = in1 + out
    print("1. Without cache")
    print(f"   input : {n} x {input_tok} / 1M x {price['input']} = {usd(in1)}")
    print(f"   output: {n} x {output_tok} / 1M x {price['output']} = {usd(out)}")
    print(f"   total : {usd(total1)}   (output = {out / total1:.0%} of the bill)\n")

    # 2. System prompt cached: 1 cache write, n-1 cache reads, user part always fresh
    write = a.system / MTOK * price["cache_write"]
    reads = (n - 1) * a.system / MTOK * price["cache_read"]
    fresh = n * a.user / MTOK * price["input"]
    in2 = write + reads + fresh
    total2 = in2 + out
    print("2. With cached system prompt")
    print(f"   cache write: 1 x {a.system} / 1M x {price['cache_write']} = {usd(write)}")
    print(f"   cache read : {n - 1} x {a.system} / 1M x {price['cache_read']} = {usd(reads)}")
    print(f"   user input : {n} x {a.user} / 1M x {price['input']} = {usd(fresh)}")
    print(f"   output     : unchanged = {usd(out)}")
    print(f"   total      : {usd(total2)}   (saved {usd(total1 - total2)}, only on input)\n")

    # 3. Cache + Batch API
    if a.batch_discount <= 0:
        print("3. Batch API: not supported for this model / not applied.")
    else:
        total3 = total2 * (1 - a.batch_discount)
        print(f"3. Cache + Batch API ({a.batch_discount:.0%} off input and output)")
        print(f"   total : {usd(total2)} x {1 - a.batch_discount:g} = {usd(total3)}")

    share = out / total2
    print(f"\nWith cache, output is {share:.0%} of the bill. Caching only touches input; "
          "output stays the same in every variant except Batch.")

if __name__ == "__main__":
    main()
