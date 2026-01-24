import doctest
import esets
import pytest


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


def test_wholes():
    w = esets.Wholes()
    assert 42 in w
    assert 3.14 not in w


def test_doctests():
    doctest.testfile("docTest.txt")
    doctest.testfile("README.md")
    doctest.testfile("FLOAT64S.md")
