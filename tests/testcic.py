import sys
import os.path
import traceback
import numpy

d = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.append(d)
import cic
def test_cic1():
    mesh = numpy.zeros((2, 2))
    pos = [[-.1, 0.0]]
    cic.cic(pos, mesh, boxsize=2.0)
    assert numpy.allclose(
            mesh, 
            [[ 0.9,  0. ],
             [ 0.1,  0. ]]
            )

def test_cic2():
    mesh = numpy.zeros((2, 2))
    pos = [[.1, 0.0]]
    cic.cic(pos, mesh, boxsize=2.0)
    assert numpy.allclose(
            mesh, 
            [[ 0.9,  0. ],
             [ 0.1,  0. ]]
            )

def test_cic3():
    mesh = numpy.zeros((2, 2))
    pos = [[0.0, 0.1]]
    cic.cic(pos, mesh, boxsize=2.0)
    assert numpy.allclose(
            mesh, 
            [[ 0.9,  0.1 ],
             [ 0.0,  0. ]]
            )

def test_cic4():
    mesh = numpy.zeros((2, 2))
    pos = [[0.0, -0.1]]
    cic.cic(pos, mesh, boxsize=2.0)
    assert numpy.allclose(
            mesh, 
            [[ 0.9,  0.1 ],
             [ 0.0,  0. ]]
            )

def test_cic5():
    mesh = numpy.zeros((2, 2))
    pos = [[1.1, 0.0]]
    cic.cic(pos, mesh, boxsize=2.0)
    assert numpy.allclose(
            mesh, 
            [[ 0.1,  0.0 ],
             [ 0.9,  0. ]]
            )

def test_cic6():
    mesh = numpy.zeros((2, 2))
    pos = [[1.1, 2.0]]
    cic.cic(pos, mesh, boxsize=2.0)
    assert numpy.allclose(
            mesh, 
            [[ 0.1,  0.0 ],
             [ 0.9,  0. ]]
            )

test_cic1()
test_cic2()
test_cic3()
test_cic4()
test_cic5()
test_cic6()
test_cic5()
