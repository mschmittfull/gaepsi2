"""
   Domain Decomposition in Gaepsi

    currently we have a GridND decomposition algorithm.

"""
from mpi4py import MPI
import numpy

class Rotator(object):
    def __init__(self, comm):
        self.comm = comm
    def __enter__(self):
        self.comm.Barrier()
        for i in range(self.comm.rank):
            self.comm.Barrier()
    def __exit__(self, type, value, tb):
        for i in range(self.comm.rank, self.comm.size):
            self.comm.Barrier()
        self.comm.Barrier()

class Layout(object):
    """ A global all to all communication layout 
        
    """
    def __init__(self, comm, sendcounts, indices, recvcounts=None):
        """
        sendcounts is the number of items to send
        indices is the indices of the items in the data array.
        """

        self.comm = comm
        assert self.comm.size == sendcounts.shape[0]

        self.sendcounts = numpy.array(sendcounts, order='C')
        self.recvcounts = numpy.empty_like(self.sendcounts, order='C')

        self.sendoffsets = numpy.zeros_like(self.sendcounts, order='C')
        self.recvoffsets = numpy.zeros_like(self.recvcounts, order='C')

        if recvcounts is None:
            # calculate the recv counts array
            # ! Alltoall
            self.comm.Barrier()
            self.comm.Alltoall(self.sendcounts, self.recvcounts)
            self.comm.Barrier()
        else:
            self.recvcounts = recvcounts
        self.sendoffsets[1:] = self.sendcounts.cumsum()[:-1]
        self.recvoffsets[1:] = self.recvcounts.cumsum()[:-1]

        self.oldlength = self.sendcounts.sum()
        self.newlength = self.recvcounts.sum()

        self.indices = indices

    def exchange(self, data):
        """ exchange the data globally according to the layout
            data shall be of the same length of the input position
            that builds the layout
        """
        # lets check the data type first
        dtypes = self.comm.allgather(data.dtype.str)
        if len(set(dtypes)) != 1:
            raise TypeError('dtype of input differ on different ranks. %s' %
                    str(dtypes))

        #build buffer
        # Watch out: 
        # take produces C-contiguous array, 
        # friendly to alltoallv.
        # fancy indexing does not always return C_contiguous
        # array (2 days to realize this!)
        
        buffer = data.take(self.indices, axis=0)

        newshape = list(data.shape)
        newshape[0] = self.newlength

        # build a dtype for communication
        # this is to avoid 2GB limit from bytes.
        duplicity = numpy.product(numpy.array(data.shape[1:], 'intp')) 
        itemsize = duplicity * data.dtype.itemsize
        dt = MPI.BYTE.Create_contiguous(itemsize)
        dt.Commit()

        recvbuffer = numpy.empty(newshape, dtype=data.dtype, order='C')
        self.comm.Barrier()

        # now fire
        rt = self.comm.Alltoallv((buffer, (self.sendcounts, self.sendoffsets), dt), 
                            (recvbuffer, (self.recvcounts, self.recvoffsets), dt))
        dt.Free()
        self.comm.Barrier()
        return recvbuffer

class GridND(object):
    """
        ND domain decomposition on a uniform grid
    """
    
    from _domain import gridnd_fill as _fill
    _fill = staticmethod(_fill)
    @staticmethod
    def _digitize(data, bins):
        if len(data) == 0:
            return numpy.empty((0), dtype='intp')
        else:
            return numpy.digitize(data, bins)

    def __init__(self, 
            grid,
            comm=MPI.COMM_WORLD,
            periodic=True):
        """ 
            grid is a list of  grid edges. 
            grid[0] or pos[:, 0], etc.
        
            grid[i][-1] are the boxsizes
            the ranks are set up into a mesh of 
                len(grid[0]) - 1, ...
        """
        self.dims = numpy.array([len(g) - 1 for g in grid], dtype='int32')
        self.grid = numpy.asarray(grid)
        self.periodic = periodic
        self.comm = comm
        assert comm.size == numpy.product(self.dims)
        rank = numpy.unravel_index(self.comm.rank, self.dims)

        self.myrank = numpy.array(rank)
        self.mystart = numpy.array([g[r] for g, r in zip(grid, rank)])
        self.myend = numpy.array([g[r + 1] for g, r in zip(grid, rank)])

    def decompose(self, pos, smoothing=0):
        """ decompose the domain according to pos,

            smoothing is the size of a particle:
                any particle that intersects the domain will
                be transported to the domain.

            returns a Layout object that can be used
            to exchange data
        """

        # we can't deal with too many points per rank, by  MPI
        assert len(pos) < 1024 * 1024 * 1024 * 2
        posT = numpy.asarray(pos).T

        Npoint = len(pos)
        Ndim = len(self.dims)
        counts = numpy.zeros(self.comm.size, dtype='int32')
        periodic = self.periodic

        if Npoint != 0:
            sil = numpy.empty((Ndim, Npoint), dtype='i2', order='C')
            sir = numpy.empty((Ndim, Npoint), dtype='i2', order='C')
            for j in range(Ndim):
                dim = self.dims[j]
                if periodic:
                    tmp = numpy.remainder(posT[j], self.grid[j][-1])
                else:
                    tmp = posT[j]
                sil[j, :] = self._digitize(tmp - smoothing, self.grid[j]) - 1
                sir[j, :] = self._digitize(tmp + smoothing, self.grid[j])
                if not periodic:
                    numpy.clip(sil[j], 0, dim, out=sil[j])
                    numpy.clip(sir[j], 0, dim, out=sir[j])

            self._fill(0, counts, self.dims, sil, sir, periodic)

            # now lets build the indices array.
            indices = self._fill(1, counts, self.dims, sil, sir, periodic)
            indices = numpy.array(indices, copy=False)
        else:
            indices = numpy.empty(0, dtype='int32')

        # create the layout object
        layout = Layout(
                comm=self.comm,
                sendcounts=counts,
                indices=indices)

        return layout

