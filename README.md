# xhashdb

Hash → name pairs for Call of Duty. XHash is the engine's name for the 64-bit FNV-1a hashes it
uses in place of strings. Plain CSV. Nothing goes in unless the name hashes to the value.

## Layout

```
csv/iw/         Modern Warfare II (IW9) and newer
csv/treyarch/   Black Ops 4 and Cold War
csv/vanguard/   Vanguard
tools/          hashing.py (the functions), validate.py (check or add rows)
```

One file per kind of name. Every file is two columns, `hash,name`.

Names are stored exactly as the game hashes them, trailing spaces included where the hash needs
them.

## Hash functions

All FNV-1a, 64-bit: `h = (h XOR byte) * prime`. The "secure" ones fold the first character into the
offset, then a 16-byte secret, then the rest of the name.

| name | offset | prime | input | notes |
|---|---|---|---|---|
| asset | 0x47F5817A5EF961BA | 0x100000001B3 | lowercase, `\` → `/` | 63-bit result; IW line assets |
| fnv | 0xCBF29CE484222325 | 0x100000001B3 | as written | Treyarch assets, bones, aliases; `fnv_lower` lowercases first |
| id | 0x1C2F2E3C8A257D07 | 0x10000000233 | lowercase, `\` → `/` | secure; the newer script hash |
| jup_scr | 0x79D6530B0BB9B5D1 | 0x10000000233 | lowercase, `\` → `/` | script names in MWII, MWIII |
| dvar | 0xD86A3B09566EBAAC | 0x10000000233 | lowercase, `\` → `/` | secure |
| dvar_vanguard | per first character | 0x10000000233 | lowercase, `\` → `/` | Vanguard only; secret unknown, so the constants are listed instead |
| omnvar | 0xAE13891B49D39E49 | 0x100000002C1 | as written | |
| omnvar_salted | 0xCBF28CE593123345 | 0x100000002C1 | lowercase, `\` → `/` | secure |

`python tools/hashing.py some_name` prints a name under each one.

## Contributing

You don't need to know which function a name uses. Give `hash,name` and the checker works it out.

Open an issue with the **Name submission** template and paste your rows, one per line:

```
AF199842C30AB910,r_hudblurexcludeinworld
7251693DE3E56C8F,stateinitsavexuidofuwarning
```

A bot checks every row, files the good ones, commits and closes the issue. Failures come back on
the issue with the reason. Edit the issue to retry.

Or send a pull request adding rows to whichever file under `csv/` fits the name. Guessing is fine,
CI tells you which function the name actually verified under. If every added row passes and you
only touched `csv/`, the PR merges itself.

Rows get rejected when:

- the hash isn't 16 hex digits
- the name doesn't hash to that value under any of our functions. Casing counts, and a trailing
  space is part of the name if the hash says so
- both halves of the hash are tiny, like `000000010000002B`. That's a table index, not a hash, and
  any "name" for it was brute-forced
- it's already in, under any file

If you've worked out a function we don't have, add it to `tools/hashing.py` with its offset, prime
and input handling, plus a hundred or so `hash,name` pairs that verify under it and nothing else.
