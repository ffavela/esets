import doctest
import esets
import pytest
import random


def test_evens():
    e = esets.Evens()
    assert 8 in e
    assert 2**(10**5) in e
    assert 5 not in e
    assert 2.5 not in e
    assert e.index(1234343243242342340) == 617171621621171170
    assert -6 not in e
    assert e.index(2*10**100) == 10**100
    assert e[1] == 2
    assert e[10] == 20
    assert e[617171621621171170] == 1234343243242342340
    with pytest.raises(ValueError):
        len(e)
    with pytest.raises(ValueError, match='Aleph_0 infinite'):
        len(e)
    slice_err = 'slice indices must be integers or None'
    with pytest.raises(TypeError, match=slice_err):
        e['frank'::]
    with pytest.raises(TypeError, match=slice_err):
        e[:'fermi':]
    with pytest.raises(TypeError, match=slice_err):
        e[::'feynman']
    with pytest.raises(TypeError, match=slice_err):
        e['some':'error':'raised']
    with pytest.raises(ValueError, match='slice step cannot be zero'):
        e[::0]
    with pytest.raises(TypeError, match='Need a slice or an integer'):
        e['frank']
    with pytest.raises(TypeError, match='Values need to be integers.'):
        esets.Evens('frank')


def test_wholes():
    w = esets.Wholes()
    assert 42 in w
    assert 3.14 not in w


def test_doctests():
    doctest.testfile("docTest.txt")
    doctest.testfile("README.md")
    doctest.testfile("FLOAT64S.md")


def test_random_EvensList():
    e = esets.Evens()
    rsign = lambda: random.choice((1, -1))
    smallest = 10
    rval = lambda x: random.randint(0, x*3//2) * rsign()
    ranI = random.randint(smallest, 100)
    for r in range(1000):
        testList = [2*i for i in range(ranI)]
        listLen = len(testList)
        le = e[:listLen]
        assert list(le) == testList
        rstart = rval(listLen)
        rstop = rval(listLen)
        rstep = rval(listLen)
        if rstep != 0:
            assert list(le[rstart:rstop:rstep]) == \
                testList[rstart:rstop:rstep]
        else:
            with pytest.raises(ValueError):
                le[rstart:rstop:rstep]

def test_random_EvensRepr():
    e = esets.Evens()
    ff = e.format_funct
    max_val = e.repr_start_max  # 4
    end_max = e.repr_end_max  # 4
    rsign = lambda: random.choice((1, -1))
    smallest = 10
    rval = lambda x: random.randint(0, x*3//2) * rsign()
    ranI = random.randint(smallest, 100)
    for r in range(1000):
        testList = [2*i for i in range(ranI)]
        listLen = len(testList)
        le = e[:listLen]
        assert list(le) == testList
        rstart = rval(listLen)
        rstop = rval(listLen)
        rstep = rval(listLen)
        if rstep != 0:
            tlen = len(testList[rstart:rstop:rstep])
            testListSliced = testList[rstart:rstop:rstep]
            reprKernel = '(' +\
                ', '.join([ff(v) for v in testListSliced[:max_val]]) +\
                '...' +\
                ', '.join([ff(v) for v in testListSliced[end_max:]]) + ')'
            if max_val + end_max >= tlen:
                reprKernel = str(tuple(testListSliced))
                if len(testListSliced) == 1:
                    reprKernel = f'({testListSliced[0]})'
                expectedRepr = f'<esets.Evens* {reprKernel}>'
                assert expectedRepr == str(le[rstart:rstop:rstep])
        else:
            with pytest.raises(ValueError):
                le[rstart:rstop:rstep]
