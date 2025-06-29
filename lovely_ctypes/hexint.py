"""Fixed-width integer"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_hexint.ipynb.

# %% auto 0
__all__ = ['ctypes_int_types', 'ctypes_signed_types', 'hexint', 'asciiint', 'HexInt', 'NamedInt', 'make_named_int']

# %% ../nbs/00_hexint.ipynb 3
import ctypes

# %% ../nbs/00_hexint.ipynb 4
ctypes_int_types = (
    ctypes.c_int8, ctypes.c_int16, ctypes.c_int32, ctypes.c_int64,
    ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint64,
    ctypes.c_bool, ctypes.c_void_p,
)

ctypes_signed_types = {
    ctypes.c_int8, ctypes.c_int16, ctypes.c_int32, ctypes.c_int64
}

# %% ../nbs/00_hexint.ipynb 6
def hexint(value, bits):
    "Returns the value as a hex string (with leading 0s, without 0x prefix)"
    assert bits > 0
    assert (bits & (bits - 1)) == 0, f"Bits must be a power of 2, got {bits}"
    assert isinstance(value, int), f"Expected int or None, got {type(value)}"
    mask = (1 << bits) - 1
    return f"{value&mask :0{bits // 4}X}"


# %% ../nbs/00_hexint.ipynb 9
def asciiint(value: int, bits: int = 8):
    if bits < 8: raise ValueError("to_ascii() requires the value to be at least 8 bits long")
    bytes_count = (bits + 7) // 8

    result = ""
    for i in range(bytes_count):
        byte_val = (value >> (i * 8)) & 0xFF
        result = (chr(byte_val) if 32 <= byte_val <= 126 else '.') + result
    return result

# %% ../nbs/00_hexint.ipynb 12
class HexInt(int):
    def __new__(cls, value:int|None, bits:int=32, signed:bool=False):
        assert bits > 0
        assert (bits & (bits - 1)) == 0, f"Bits must be a power of 2, got {bits}"
        assert isinstance(value, (int, type(None))), f"Expected int or None, got {type(value)}"

        if value is None: value = 0

        assert value >= 0 or signed, f"Negative values are only allowed for signed types, got {value}"
        max_val = (1 << (bits - 1)) - 1 if signed else (1 << bits) - 1
        min_val = -(1 << (bits - 1)) if signed else 0
        assert min_val <= value <= max_val, f"Value {value} doesn't fit in {bits} bits range [{min_val}, {max_val}]"

        i = super().__new__(cls, int(value))
        i.bits, i.signed = bits, signed
        return i

    @classmethod
    def from_ctype(cls, x:ctypes_int_types):
        """
        Creates a HexInt from a ctypes int/bool/pointer type
        """
        assert type(x) in ctypes_int_types, f"Unexpected type {type(x)}, should be in {ctypes_int_types}"
        bits = 1 if type(x) is ctypes.c_bool else ctypes.sizeof(x) * 8
        return cls(x.value, bits=bits, signed=type(x) in ctypes_signed_types)

    def hex(self): return hexint(self, self.bits)
    def ascii(self): return asciiint(self, self.bits)

    def __repr__(self):
        if self.bits == 1: return str(int(self))
        return "0x" + self.hex() + (f" ({int(self)})" if self.signed and self < 0 else '')

# %% ../nbs/00_hexint.ipynb 19
class NamedInt(int):
    _raw: int
    def __new__(cls, val):
       c = super().__new__(cls, val)
       c._raw = val
       return c

    def __repr__(self): return f"{self.__class__.__name__}({self._raw})"

def make_named_int(name, val):
   return type(name, (NamedInt,), {})(val)
