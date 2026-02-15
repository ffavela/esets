from eset import Eset
from math import isqrt, copysign
import struct
import sys
from fractions import Fraction


class Evens(Eset):
    """Something that contains all positive Integer evens"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.VALUE = 2

    def contains(self, val):
        if not isinstance(val, int):
            return False

    def inverse_fun(self, val):
        return val // self.VALUE

    def direct_function(self, i):
        return i * self.VALUE

    def stop_init(self):
        return None


class Multiples(Eset):
    """Something that contains all positive multiples of a number"""
    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.VALUE = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            self.VALUE = args[0]
            super().__init__(xtra_params=(self.VALUE,))
        else:
            self.VALUE = 2
            super().__init__(*args, xtra_params=(self.VALUE,))

        if not isinstance(self.VALUE, int):
            raise ValueError("VALUE has to be an integer")

        if self.VALUE == 0:
            raise ValueError("VALUE cannot be zero")

    def contains(self, val):
        if not isinstance(val, int):
            return False

    def inverse_fun(self, val):
        return val // self.VALUE

    def direct_function(self, i):
        return i * self.VALUE

    def stop_init(self):
        return None


class Negatives(Eset):
    """Something that contains the negative Integer numbers"""
    def contains(self, val):
        if not isinstance(val, int):
            return False

    def inverse_fun(self, val):
        return -(val+1)

    def direct_function(self, i):
        return -(i+1)

    def stop_init(self):
        return None


class Integers(Eset):
    """Something that contains all Integers"""
    def contains(self, val):
        if not isinstance(val, int):
            return False

    def inverse_fun(self, val):
        if val > 0:
            x = 2*val - 1
        else:
            x = -2*val
        return x

    def direct_function(self, i):
        return (-1)**(i+1) * ((i+1)//2)

    def stop_init(self):
        return None


class Squares(Eset):
    """Something that contains all positive Integer squares"""
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.VALUE = 2

    def contains(self, val):
        if not isinstance(val, int):
            return False

    def inverse_fun(self, val):
        return isqrt(val)

    def direct_function(self, i):
        return i ** self.VALUE

    def stop_init(self):
        return None


class Wholes(Eset):
    """Something that contains the Whole numbers"""
    def contains(self, val):
        if not isinstance(val, int):
            return False

    def inverse_fun(self, val):
        return val

    def direct_function(self, i):
        return i

    def stop_init(self):
        return None


class Float64_tpls(Eset):
    """Something that contains all the Float 64 numbers using the IEEE
    754 double precision format as tuples with 3 integers, naming them
    tpls

    """
    def contains(self, val):
        if not isinstance(val, tuple):
            return False
        s_bit, exponent, significand = val
        if not isinstance(s_bit, int) or\
           not isinstance(exponent, int) or\
           not isinstance(significand, int):
            return False
        if s_bit not in (0, 1):
            return False
        if not 0 <= exponent < 2**11:  # -1=1+2^2+...+2^10
            return False
        if not 0 <= significand < 2**52:  # -1=1+2^2+...+2^51
            return False

    def inverse_fun(self, val):
        s_bit, exponent, significand = val
        i = 2*(exponent * 2**52 + significand)
        if s_bit:
            i += 1
        return i

    def get_e_s(self, i):
        e, s = 0, i
        for j in range(63, 51, -1):
            e += (s // 2**j) * 2**(j-52)
            s %= 2**j
        return e, s

    def direct_function(self, i):
        if (-1)**(i+1) < 0:
            s_bit = 0
        else:
            s_bit = 1
        v = i//2
        exponent, significand = self.get_e_s(v)
        return (s_bit, exponent, significand)

    def stop_init(self):
        return 2**64  # -1 == 1 + 2^1 + 2^2 + ... + 2^63


class Float64s(Eset):
    """An Eset that contains all Float64s (AKA doubles in some
    languajes), this includes 1.0, 0.5, 0, -0, inf, -inf, nan, and
    -nan.

    Note that the IEEE 754 standard defines the infinites as having
    all ones on the bits of the exponent (2**11-1 == 2047) and all
    zeroes on the significand (i.e. 0 when seen as an integer). While
    a nan has also all ones on the exponent bits but the significand
    is not zero, we'll simply use as convention that a nan has a 1 on
    the last (rightmost) bit that is a one when viewed as a base ten
    integer (also it is simpler to enumerate this way). Also nans are
    distinguishable from each other but to the general end user they
    aren't, we'll just consider the aspect given by the sign bit hence
    the enumeration of the nan and the -nan.

    """
    def __init__(self, *args, **kwargs):
        if not self.check_if_float64_sys():
            raise NotImplementedError("The default floats aren't 64 bit")

        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.f64tpls = kwargs['xtra_params'][0]
            super().__init__(*args, **kwargs)
        elif len(args) == 1:
            self.f64tpls = args[0]
            super().__init__(xtra_params=(self.f64tpls,))
        else:
            f64tpls = Float64_tpls()
            minus_nan_tpl_idx = f64tpls.index((1, 2047, 1))
            self.f64tpls = f64tpls[:minus_nan_tpl_idx+1]
            super().__init__(*args, xtra_params=(self.f64tpls,))

    def stop_init(self):
        """This happens to be the same as
        f64tpls[:f64tpls.index((1, 2047, 1))+1].len() ==
        2*(2**63-2**52+2) == 2*(2**63-1-(2**52-1)+2) Note that the
        +2 inside the parenths is for the inf and the nan. And the 2*
        coefficient is for considering the negatives too.

        """
        return 18437736874454810628

    def contains(self, val):
        if isinstance(val, int):
            if int(float(val)) != val:
                return False
        if isinstance(val, Fraction):
            if Fraction(float(val)) != val:
                return False
        # Delegating the rest to Float64_tpls
        bintpl = self.float2bintpl(val)
        tpl = self.bintpl2tpl(bintpl)
        return tpl in self.f64tpls

    def check_if_float64_sys(self):
        float64_dict = {"dig": 15,
                        "epsilon": 2.220446049250313e-16,
                        "mant_dig": 53,
                        "max": 1.7976931348623157e+308,
                        "max_10_exp": 308,
                        "max_exp": 1024,
                        "min": 2.2250738585072014e-308,
                        "min_10_exp": -307,
                        "min_exp": -1021,
                        "n_fields": 11,
                        "n_sequence_fields": 11,
                        "n_unnamed_fields": 0,
                        "radix": 2,
                        "rounds": 1
                        }

        for key in dir(sys.float_info):
            if not key.startswith('_'):
                if key in ['count', 'index']:
                    continue
                value = getattr(sys.float_info, key)
                if float64_dict[key] != value:
                    return False
        return True

    def binstr2bintpl(self, binstr):
        n_sign = 1
        n_exponent = 11
        n_significand = 52
        bin_tpl = (binstr[0], binstr[n_sign:n_exponent+n_sign],
                   binstr[n_exponent+n_sign:])
        if bin_tpl[1] == n_exponent*'1' and\
           bin_tpl[2] != n_significand*'0':
            # The nan case using my convention. It is cooler, ok not
            # really I just took a poor decision early on cause I
            # didn't know any better and now I'm too afraid to start
            # changing that.
            bin_tpl = (bin_tpl[0], bin_tpl[1],
                       (n_significand-1)*'0'+'1')

        return bin_tpl

    def bintpl2tpl(self, bintpl):
        return (int(bintpl[0], 2), int(bintpl[1], 2),
                int(bintpl[2], 2))

    def tpl2bintpl(self, tpl):
        return (format(tpl[0], '01b'),
                format(tpl[1], '011b'),
                format(tpl[2], '052b'))

    def float2tpl(self, fval):
        bintpl = self.float2bintpl(fval)
        return self.bintpl2tpl(bintpl)

    def tpl2float(self, tpl):
        bintpl = self.tpl2bintpl(tpl)
        return self.bintpl2float(bintpl)

    def float2bintpl(self, fval):
        # Pack the float into 8 bytes (64 bits) using the 'd' format
        # specifier for double '!' specifies network byte order
        # (big-endian), which ensures consistency across systems
        packed_bytes = struct.pack('!d', fval)

        # Unpack the 8 bytes as a 64-bit unsigned integer ('Q' format
        # specifier) The result is a standard Python integer
        unpacked_int = struct.unpack('!Q', packed_bytes)[0]

        # Format the integer as a 64-bit binary string, zero-padded to
        # 64 digits
        binstr = format(unpacked_int, '064b')
        bin_tpl = self.binstr2bintpl(binstr)
        return bin_tpl

    def bintpl2float(self, bintpl):
        """
        Converts a bintpl to a 64-bit float.
        """
        binary_string = bintpl[0]+bintpl[1]+bintpl[2]
        # Convert the binary string to an integer
        binary_int = int(binary_string, 2)

        # Convert the integer to 8 bytes (64 bits) using big-endian
        # byte order ('>Q') The 'Q' format character is for unsigned
        # long long (8 bytes)
        binary_bytes = struct.pack('>Q', binary_int)

        # Unpack the bytes as a double (64-bit float) using big-endian
        # byte order ('>d') The 'd' format character is for a double
        float_value = struct.unpack('>d', binary_bytes)[0]

        return float_value

    def inverse_fun(self, fVal):
        bintpl = self.float2bintpl(fVal)
        tpl = self.bintpl2tpl(bintpl)
        return self.f64tpls.index(tpl)

    def direct_function(self, i):
        tpl = self.f64tpls[i]
        bintpl = self.tpl2bintpl(tpl)
        fVal = self.bintpl2float(bintpl)
        return fVal

    def __len__(self):
        return self.f64tpls.__len__()

    def len(self):
        return self.f64tpls.len()

    def __getitem__(self, key):
        """Delegating __getitem__ to the eset object f64tpls and
        creating another Float64 eset with it.

        """
        if isinstance(key, slice):
            return Float64s(xtra_params=(self.f64tpls[key],))
        elif isinstance(key, int):
            bintpl = self.tpl2bintpl(self.f64tpls[key])
            fVal = self.bintpl2float(bintpl)
            return fVal
        raise ValueError('Need a slice or an integer')

    def format_funct(self, v):
        if v != v:  # Checking if v is nan (weird I know)
            sign = copysign(1, v)
            if sign < 0:
                return '-nan'
        return f"{v:.17g}"


class IntArithProg(Eset):
    """An integer arithmetic progression eset"""
    def __init__(self, *args, **kwargs):
        if 'xtra_params' in kwargs:
            if len(kwargs['xtra_params']) != 0:
                self.COEF = kwargs['xtra_params'][0]
                self.CONS = kwargs['xtra_params'][1]
            super().__init__(*args, **kwargs)
        elif len(args) == 2:
            self.COEF = args[0]
            self.CONS = args[1]
            if not isinstance(self.COEF, int) or\
               not isinstance(self.CONS, int):
                raise ValueError("Values need to be integers")
            if self.COEF == 0:
                raise ValueError("COEF cannot be zero")
            super().__init__(xtra_params=(self.COEF, self.CONS))
        else:
            raise ValueError("Not enough arguments to initialize")

    def contains(self, val):
        if not isinstance(val, int):
            return False

    def direct_function(self, i):
        return i * self.COEF + self.CONS

    def inverse_fun(self, val):
        return (val - self.CONS) // self.COEF

    def stop_init(self):
        return None

if __name__ == '__main__':
    import doctest
    doctest.testfile("docTest.txt")
    doctest.testfile("README.md")
    # doctest.testfile("FLOAT64S.md")
