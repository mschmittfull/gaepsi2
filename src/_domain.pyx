import cython
import numpy
cimport cython
cimport numpy
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.overflowcheck(False)
@cython.nonecheck(False)
def gridnd_fill(
        int mode,
        int [::1] counts,
        int [:] adims,
        short int [:, ::1] sil,
        short int [:, ::1] sir,
        int periodic,
        ):
    """ 
        fill in the counts or return the indices 
        This really can be done with numba / hope /cyjit
    """
    # first count the sizes
    cdef int patchsize = 0
    cdef int p[32]
    cdef int strides[32]
    cdef int dims[32]
    cdef numpy.int32_t [::1] offset = None
    cdef int i
    cdef int j
    cdef int jj
    cdef int k
    cdef int t
    cdef int [::1] indices = None
    cdef int Nrank
    cdef int Ndim
    cdef int Npoint

    Nrank = counts.shape[0]
    Ndim = adims.shape[0]
    Npoint = sil.shape[1]

    if mode == 1:
        offset = numpy.empty(Nrank + 1, dtype='int32', order='C')
        offset[0] = 0
        for i in range(1, Nrank + 1):
            offset[i] = offset[i - 1] + counts[i - 1]
        totalsize = offset[Nrank]
        indices = numpy.empty(totalsize, dtype='int32', order='C')

    for j in range(Ndim):
        dims[j] = adims[j]

    strides[Ndim -1 ] = 1
    for j in range(Ndim - 2, -1, -1):
        strides[j] = strides[j + 1] * dims[j + 1]
    cdef numpy.intp_t target
    for i in range(Npoint):
        patchsize = 1
        for j in range(Ndim):
            patchsize *= sir[j, i] - sil[j, i]
            p[j] = sil[j, i]
        for k in range(patchsize):
            target = 0
            for j in range(Ndim):
                t = p[j]
                if periodic:
                    while t >= dims[j]:
                        t -= dims[j]
                    while t < 0:
                        t += dims[j]
                target = target + t * strides[j]
            if mode == 0:
                counts[target] += 1
            else:
                indices[offset[target]] = i
                offset[target] += 1
            p[Ndim - 1] += 1
            # advance
            for jj in range(Ndim-1, 0, -1):
                if p[jj] == sir[jj, i]:
                    p[jj] = sil[jj, i]
                    p[jj - 1] += 1
                else:
                    break
    return indices

