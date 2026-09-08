"""The hash functions. README.md says what each one is and where it is used."""
import sys
from functools import partial

M64 = (1 << 64) - 1
MASK63 = M64 >> 1

PRIME = 0x100000001B3          # FNV-1a 64
PRIME_SCR = 0x10000000233      # script and dvar
PRIME_OMNVAR = 0x100000002C1

OFF_FNV = 0xCBF29CE484222325
OFF_ASSET = 0x47F5817A5EF961BA
OFF_JUP_SCR = 0x79D6530B0BB9B5D1
OFF_ID = 0x1C2F2E3C8A257D07
OFF_DVAR = 0xD86A3B09566EBAAC
OFF_OMNVAR = 0xAE13891B49D39E49
OFF_OMNVAR_SALTED = 0xCBF28CE593123345

SECRET_ID = "zt@f3yp(d[kkd=_@"
SECRET_DVAR = "q6n-+7=tyytg94_*"
SECRET_OMNVAR = "gvbs9*vpm@mh@krh"

DVAR_VANGUARD_BASE = {
    "a": 0xCB916A83C4E2C1FF,
    "b": 0x0A7346F232F08A1A,
    "c": 0x6F089DD565F89E95,
    "d": 0xC95B1F03C4378A70,
    "e": 0xB2298F9C0D67123B,
    "f": 0xE3F1CD132FA3E9E6,
    "g": 0x1117FEA825AF9271,
    "h": 0xF5B21BDBA19672AC,
    "i": 0xF22A8A5B005B2C47,
    "j": 0xBB734DC77DBA2682,
    "k": 0xD445A5F1C54FD0FD,
    "l": 0x210E062374385478,
    "m": 0xBE892DC96DBEA363,
    "n": 0xFD0B3DB05C5751CE,
    "o": 0x6CE67972894E8F79,
    "p": 0x9BB2FBC2F42C3B54,
    "r": 0x8A43A0A843922A2A,
    "s": 0xE3EAD09E517AE525,
    "t": 0x4C6D2A596F87E580,
    "u": 0xA3FBA9FF0FF5F98B,
    "v": 0xD567E632548EBBF6,
    "w": 0x9640CCE1A1EA0E41,
    "x": 0xCD3122D9F8CADC3C,
}


def _fnv(text, h, prime):
    for ch in text:
        h = ((h ^ (ord(ch) & 0xFF)) * prime) & M64
    return h


def _game_lower(text):
    """The engine's fold: ASCII upper to lower, backslash to forward slash."""
    return "".join(chr(o + 32) if 65 <= (o := ord(c)) <= 90 else ("/" if c == "\\" else c)
                   for c in text)


def _fold(text, h, prime):
    return _fnv(_game_lower(text), h, prime)


def _secure(secret, offset, prime, name):
    if not name:
        return 0
    head = _fold(secret, _fold(name[0], offset, prime), prime)
    return _fold(name[1:], head, prime)


def _dvar_vanguard(name):
    base = DVAR_VANGUARD_BASE.get(_game_lower(name[:1]))
    return None if base is None else _fold(name[1:], base, PRIME_SCR)


FAMILIES = {
    "asset": lambda n: _fold(n, OFF_ASSET, PRIME) & MASK63,
    "fnv": lambda n: _fnv(n, OFF_FNV, PRIME),
    "fnv_lower": lambda n: _fnv(n.lower(), OFF_FNV, PRIME),
    "id": partial(_secure, SECRET_ID, OFF_ID, PRIME_SCR),
    "jup_scr": lambda n: _fold(n, OFF_JUP_SCR, PRIME_SCR),
    "dvar": partial(_secure, SECRET_DVAR, OFF_DVAR, PRIME_SCR),
    "dvar_vanguard": _dvar_vanguard,
    "omnvar": lambda n: _fnv(n, OFF_OMNVAR, PRIME_OMNVAR),
    "omnvar_salted": partial(_secure, SECRET_OMNVAR, OFF_OMNVAR_SALTED, PRIME_OMNVAR),
}


def verify(hash_value, name):
    """Every function under which `name` reproduces `hash_value`. '~63' means the low 63 bits only."""
    out = []
    for fam, f in FAMILIES.items():
        v = f(name)
        if v == hash_value:
            out.append(fam)
        elif v is not None and v & MASK63 == hash_value & MASK63:
            out.append(fam + "~63")
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(arg)
        for fam, f in FAMILIES.items():
            v = f(arg)
            print("  %-14s %s" % (fam, "-" if v is None else "%016X" % v))
