"""
Data sources classes and their associated functions for mlab.
"""

# Author: Gael Varoquaux <gael.varoquaux@normalesup.org>
#         Prabhu Ramachandran
# Copyright (c) 2007-2008, Enthought, Inc. 
# License: BSD Style.

import numpy

from enthought.traits.api import (HasTraits, Instance, Array, Either,
            on_trait_change)
from enthought.tvtk.api import tvtk
from enthought.tvtk.common import camel2enthought

from enthought.mayavi.sources.array_source import ArraySource
from enthought.mayavi.core.registry import registry

import tools
from engine_manager import engine_manager

__all__ = [ 'vector_scatter', 'vector_field', 'scalar_scatter',
    'scalar_field', 'line_source', 'array2d_source', 'grid_source', 'open'
]


################################################################################
# `MlabSource` class.
################################################################################ 
class MlabSource(HasTraits):
    """
    This class represents the base class for all mlab sources.  These
    classes allow a user to easily update the data without having to
    recreate the whole pipeline.
    """

    # The TVTK dataset we manage.
    dataset = Instance(tvtk.DataSet)

    # The Mayavi data source we manage.
    m_data = Instance(HasTraits)

    ######################################################################
    # `MGlyphSource` interface.
    ######################################################################
    def create(self):
        """Function to create the data from input arrays etc.
        """
        raise NotImplementedError()

    def update(self):
        """Update the visualization.

        This is to be called after the data of the visualization has
        changed.
        """
        self.dataset.modified()
        self.m_data.data_changed = True

    ######################################################################
    # Non-public interface.
    ######################################################################
    def _m_data_changed(self, ds):
        if not hasattr(ds, 'mlab_source'):
            ds.add_trait('mlab_source', Instance(MlabSource))
        ds.mlab_source = self


ArrayOrNone = Either(None, Array)

################################################################################
# `MGlyphSource` class.
################################################################################ 
class MGlyphSource(MlabSource):
    """
    This class represents a glyph data source for Mlab objects and
    allows the user to set the x, y, z, scalar/vector attributes.
    """

    # The x, y, z and points of the glyphs.
    x = ArrayOrNone
    y = ArrayOrNone
    z = ArrayOrNone
    points = ArrayOrNone

    # The scalars shown on the glyphs.
    scalars = ArrayOrNone

    # The u, v, w components of the vector and the vectors.
    u = ArrayOrNone
    v = ArrayOrNone
    w = ArrayOrNone
    vectors = ArrayOrNone

    ######################################################################
    # `MGlyphSource` interface.
    ######################################################################
    def create(self):
        """Creates the dataset afresh.  Call this after you have set the
        x, y, z, scalars/vectors."""

        vectors = self.vectors
        scalars = self.scalars
        points = self.points
        x, y, z = self.x, self.y, self.z
        if points is None or len(points) == 0:
            points = numpy.c_[x.ravel(), y.ravel(), z.ravel()].ravel()
            points.shape = (points.size/3, 3)
            self.set(points=points, trait_change_notify=False)
    
        u, v, w = self.u, self.v, self.w
        if vectors is None or len(vectors) == 0:
            if u is not None and len(u) > 0:
                vectors = numpy.c_[u.ravel(), v.ravel(),
                                   w.ravel()].ravel()
                vectors.shape = (vectors.size/3, 3)
                self.set(vectors=vectors, trait_change_notify=False)

        if vectors is not None and len(vectors) > 0:
            assert len(points) == len(vectors)
        if scalars is not None and len(scalars) > 0:
            assert len(points) == len(scalars)
        
        # Create the dataset.
        polys = numpy.arange(0, len(points), 1, 'l')
        polys = numpy.reshape(polys, (len(points), 1))
        pd = tvtk.PolyData(points=points, polys=polys)

        if self.vectors is not None:
            pd.point_data.vectors = self.vectors
            pd.point_data.vectors.name = 'vectors'
        if self.scalars is not None:
            pd.point_data.scalars = self.scalars
            pd.point_data.scalars.name = 'scalars'

        self.dataset = pd

    ######################################################################
    # Non-public interface.
    ######################################################################
    def _x_changed(self, x):
        self.points[:,0] = x
        self.update()

    def _y_changed(self, y):
        self.points[:,1] = y
        self.update()
    
    def _z_changed(self, z):
        self.points[:,2] = z
        self.update()

    def _u_changed(self, u):
        self.vectors[:,0] = u
        self.update()

    def _v_changed(self, v):
        self.vectors[:,1] = v
        self.update()
    
    def _w_changed(self, w):
        self.vectors[:,2] = w 
        self.update()

    def _points_changed(self, p):
        self.dataset.points = p
        self.update()

    def _scalars_changed(self, s):
        self.dataset.point_data.scalars = s
        self.dataset.point_data.scalars.name = 'scalars'
        self.update()

    def _vectors_changed(self, v):
        self.dataset.point_data.vectors = v
        self.dataset.point_data.vectors.name = 'vectors'
        self.update()


################################################################################
# `MArraySource` class.
################################################################################ 
class MArraySource(MlabSource):
    """
    This class represents an array data source for Mlab objects and
    allows the user to set the x, y, z, scalar/vector attributes.
    """

    # The x, y, z arrays for the volume.
    x = ArrayOrNone
    y = ArrayOrNone
    z = ArrayOrNone

    # The scalars shown on the glyphs.
    scalars = ArrayOrNone

    # The u, v, w components of the vector and the vectors.
    u = ArrayOrNone
    v = ArrayOrNone
    w = ArrayOrNone
    vectors = ArrayOrNone

    ######################################################################
    # `MGlyphSource` interface.
    ######################################################################
    def create(self):
        """Creates the dataset afresh.  Call this after you have set the
        x, y, z, scalars/vectors."""
        vectors = self.vectors
        scalars = self.scalars
        x, y, z = self.x, self.y, self.z
    
        u, v, w = self.u, self.v, self.w
        if vectors is None or len(vectors) == 0:
            if u is not None and len(u) > 0:
                #vectors = numpy.concatenate([u[..., numpy.newaxis],
                #                             v[..., numpy.newaxis],
                #                             w[..., numpy.newaxis] ],
                #                axis=3)
                vectors = numpy.c_[u.ravel(), v.ravel(),
                                   w.ravel()].ravel()
                vectors.shape = (len(u), len(v), len(w), 3)
                self.set(vectors=vectors, trait_change_notify=False)

        if vectors is not None and len(vectors) > 0:
            assert len(x) == len(vectors)
        if scalars is not None and len(scalars) > 0:
            assert len(x) == len(scalars)

        dx = x[1, 0, 0] - x[0, 0, 0]
        dy = y[0, 1, 0] - y[0, 0, 0]
        dz = z[0, 0, 1] - z[0, 0, 0]
                                
        ds = ArraySource(transpose_input_array=True,
                         vector_data=vectors,
                         origin=[x.min(), y.min(), z.min()],
                         spacing=[dx, dy, dz],
                         scalar_data=scalars)
        
        self.dataset = ds.image_data
        self.m_data = ds 

    ######################################################################
    # Non-public interface.
    ######################################################################
    @on_trait_change('[x, y, z]')
    def _xyz_changed(self):
        x, y, z = self.x, self.y, self.z
        dx = x[1, 0, 0] - x[0, 0, 0]
        dy = y[0, 1, 0] - y[0, 0, 0]
        dz = z[0, 0, 1] - z[0, 0, 0]
        ds = self.dataset
        ds.origin = [x.min(), y.min(), z.min()]
        ds.spacing = [dx, dy, dz] 
        self.update()

    def _u_changed(self, u):
        self.vectors[...,0] = u
        self.m_data._vector_data_changed(self.vectors)

    def _v_changed(self, v):
        self.vectors[...,1] = v
        self.m_data._vector_data_changed(self.vectors)
    
    def _w_changed(self, w):
        self.vectors[...,2] = w
        self.m_data._vector_data_changed(self.vectors)

    def _scalars_changed(self, s):
        self.m_data.scalar_data = s

    def _vectors_changed(self, v):
        self.m_data.vector_data = v


################################################################################
# `MLineSource` class.
################################################################################ 
class MLineSource(MlabSource):
    """
    This class represents a line data source for Mlab objects and
    allows the user to set the x, y, z, scalar attributes.
    """

    # The x, y, z and points of the glyphs.
    x = ArrayOrNone
    y = ArrayOrNone
    z = ArrayOrNone
    points = ArrayOrNone

    # The scalars shown on the glyphs.
    scalars = ArrayOrNone

    ######################################################################
    # `MGlyphSource` interface.
    ######################################################################
    def create(self):
        """Creates the dataset afresh.  Call this after you have set the
        x, y, z, scalars/vectors."""
        points = self.points
        scalars = self.scalars
        x, y, z = self.x, self.y, self.z
    
        if points is None or len(points) == 0:
            points = numpy.c_[x.ravel(), y.ravel(), z.ravel()].ravel()
            points.shape = (len(x), 3)
            self.set(points=points, trait_change_notify=False)

        # Create the dataset.
        np = len(points) - 1
        lines  = numpy.zeros((np, 2), 'l')
        lines[:,0] = numpy.arange(0, np-0.5, 1, 'l')
        lines[:,1] = numpy.arange(1, np+0.5, 1, 'l')
        pd = tvtk.PolyData(points=points, lines=lines)

        if scalars is not None and len(scalars) > 0:
            assert len(x) == len(scalars)
            pd.point_data.scalars = scalars.ravel() 
            pd.point_data.scalars.name = 'scalars'

        self.dataset = pd

    ######################################################################
    # Non-public interface.
    ######################################################################
    def _x_changed(self, x):
        self.points[:,0] = x
        self.update()

    def _y_changed(self, y):
        self.points[:,1] = y
        self.update()
    
    def _z_changed(self, z):
        self.points[:,2] = z
        self.update()

    def _points_changed(self, p):
        self.dataset.points = p
        self.update()

    def _scalars_changed(self, s):
        self.dataset.point_data.scalars = s.ravel()
        self.dataset.point_data.scalars.name = 'scalars'
        self.update()

################################################################################
# `MArray2DSource` class.
################################################################################ 
class MArray2DSource(MlabSource):
    """
    This class represents a 2D array data source for Mlab objects and
    allows the user to set the x, y  and scalar attributes.
    """

    # The x, y values.
    x = ArrayOrNone
    y = ArrayOrNone

    # The scalars shown on the glyphs.
    scalars = ArrayOrNone

    # The masking array.
    mask = ArrayOrNone

    ######################################################################
    # `MGlyphSource` interface.
    ######################################################################
    def create(self):
        """Creates the dataset afresh.  Call this after you have set the
        x, y, scalars."""
        x, y, mask = self.x, self.y, self.mask
        scalars = self.scalars

        if mask is not None and len(mask) > 0:
            scalars[mask.astype('bool')] = numpy.nan
            # The NaN tric only works with floats.
            scalars = scalars.astype('float')
            self.set(scalars=scalars, trait_change_notify=False)

        if x is None or len(x) == 0:
            nx, ny = scalars.shape
            x, y = numpy.mgrid[-nx/2.:nx/2, -ny/2.:ny/2]
            z = numpy.array([0])
            self.set(x=x, y=y, z=z, trait_change_notify=False)

        dx = x[1, 0] - x[0, 0]
        dy = y[0, 1] - y[0, 0]
                                
        ds = ArraySource(transpose_input_array=True,
                         origin=[x.min(), y.min(), 0],
                         spacing=[dx, dy, 1],
                         scalar_data=scalars)
        
        self.dataset = ds.image_data
        self.m_data = ds 

    ######################################################################
    # Non-public interface.
    ######################################################################
    @on_trait_change('[x, y]')
    def _xyz_changed(self):
        x, y = self.x, self.y
        dx = x[1, 0] - x[0, 0]
        dy = y[0, 1] - y[0, 0]
        ds = self.dataset
        ds.origin = [x.min(), y.min(), 0]
        ds.spacing = [dx, dy, 1] 
        self.update()

    def _scalars_changed(self, s):
        mask = self.mask
        if mask is not None and len(mask) > 0:
            scalars[mask.astype('bool')] = numpy.nan
            # The NaN tric only works with floats.
            scalars = scalars.astype('float')
            self.set(scalars=scalars, trait_change_notify=False)
        self.m_data.scalar_data = s


################################################################################
# `MGridSource` class.
################################################################################ 
class MGridSource(MlabSource):
    """
    This class represents a grid source for Mlab objects and
    allows the user to set the x, y, scalar attributes.
    """

    # The x, y, z and points of the grid.
    x = ArrayOrNone
    y = ArrayOrNone
    z = ArrayOrNone
    points = ArrayOrNone

    # The scalars shown on the glyphs.
    scalars = ArrayOrNone

    ######################################################################
    # `MGlyphSource` interface.
    ######################################################################
    def create(self):
        """Creates the dataset afresh.  Call this after you have set the
        x, y, z, scalars/vectors."""
        points = self.points
        scalars = self.scalars
        x, y, z = self.x, self.y, self.z

        assert len(x.shape) == 2, "Array x must be 2 dimensional."
        assert len(y.shape) == 2, "Array y must be 2 dimensional."
        assert len(z.shape) == 2, "Array z must be 2 dimensional."
        assert x.shape == y.shape, "Arrays x and y must have same shape."
        assert y.shape == z.shape, "Arrays y and z must have same shape."
    
        nx, ny = x.shape
        if points is None or len(points) == 0:
            points = numpy.c_[x.ravel(), y.ravel(), z.ravel()].ravel()
            points.shape = (nx*ny, 3)
            self.set(points=points, trait_change_notify=False)

        i, j = numpy.mgrid[0:nx-1,0:ny-1]
        i, j = numpy.ravel(i), numpy.ravel(j)
        t1 = i*ny+j, (i+1)*ny+j, (i+1)*ny+(j+1)
        t2 = (i+1)*ny+(j+1), i*ny+(j+1), i*ny+j
        nt = len(t1[0])
        triangles = numpy.zeros((nt*2, 3), 'l')
        triangles[0:nt,0], triangles[0:nt,1], triangles[0:nt,2] = t1
        triangles[nt:,0], triangles[nt:,1], triangles[nt:,2] = t2

        pd = tvtk.PolyData(points=points, polys=triangles)

        if scalars is not None and len(scalars) > 0:
            if not scalars.flags.contiguous:
                scalars = scalars.copy()
                self.set(scalars=scalars, trait_change_notify=False)
            assert x.shape == scalars.shape
            pd.point_data.scalars = scalars.ravel() 
            pd.point_data.scalars.name = 'scalars'

        self.dataset = pd

    ######################################################################
    # Non-public interface.
    ######################################################################
    def _x_changed(self, x):
        nx, ny = self.x.shape
        x.shape = (nx*ny,)
        self.points[:,0] = x
        self.update()

    def _y_changed(self, y):
        nx, ny = self.x.shape
        y.shape = (nx*ny,)
        self.points[:,1] = y
        self.update()
    
    def _z_changed(self, z):
        nx, ny = self.x.shape
        z.shape = (nx*ny,)
        self.points[:,2] = z
        self.update()

    def _points_changed(self, p):
        self.dataset.points = p
        self.update()

    def _scalars_changed(self, s):
        self.dataset.point_data.scalars = s.ravel()
        self.dataset.point_data.scalars.name = 'scalars'
        self.update()



# FIXME: Add tests for new sources.


############################################################################
# Argument processing
############################################################################

def convert_to_arrays(args):
    """ Converts a list of iterables to a list of arrays or callables, 
        if needed.
    """
    args = list(args)
    for index, arg in enumerate(args):
        if not hasattr(arg, 'shape') and not callable(arg):
            args[index] = numpy.array(arg)
    return args

def process_regular_vectors(*args):
    """ Converts different signatures to (x, y, z, u, v, w). """
    args = convert_to_arrays(args)
    if len(args)==3:
        u, v, w = args
        assert len(u.shape)==3, "3D array required"
        x, y, z = numpy.indices(u.shape)
    elif len(args)==6:
        x, y, z, u, v, w = args
    elif len(args)==4:
        x, y, z, f = args
        if not callable(f):
            raise ValueError, "When 4 arguments are provided, the fourth must be a callable"
        u, v, w = f(x, y, z)
    else:
        raise ValueError, "wrong number of arguments"

    assert ( x.shape == y.shape and
            y.shape == z.shape and
            u.shape == z.shape and
            v.shape == u.shape and
            w.shape == v.shape ), "argument shape are not equal"

    return x, y, z, u, v, w

def process_regular_scalars(*args):
    """ Converts different signatures to (x, y, z, s). """
    args = convert_to_arrays(args)
    if len(args)==1:
        s = args[0]
        assert len(s.shape)==3, "3D array required"
        x, y, z = numpy.indices(s.shape)
    elif len(args)==3:
        x, y, z = args
        s = None 
    elif len(args)==4:
        x, y, z, s = args
        if callable(s):
            s = s(x, y, z)
    else:
        raise ValueError, "wrong number of arguments"

    assert ( x.shape == y.shape and
            y.shape == z.shape and
            ( s is None
                or s.shape == z.shape ) ), "argument shape are not equal"

    return x, y, z, s

def process_regular_2d_scalars(*args, **kwargs):
    """ Converts different signatures to (x, y, s). """
    args = convert_to_arrays(args)
    if len(args)==1:
        s = args[0]
        assert len(s.shape)==2, "2D array required"
        x, y = numpy.indices(s.shape)
    elif len(args)==3:
        x, y, s = args
        if callable(s):
            s = s(x, y)
    else:
        raise ValueError, "wrong number of arguments"
    assert len(s.shape)==2, "2D array required"

    if 'mask' in kwargs:
        mask = kwargs['mask']
        s[mask.astype('bool')] = numpy.nan
        # The NaN tric only works with floats.
        s = s.astype('float')

    return x, y, s


############################################################################
# Sources 
############################################################################

def vector_scatter(*args, **kwargs):
    """ Creates scattered vector data. 
    
    **Function signatures**::

        vector_scatter(u, v, w, ...)
        vector_scatter(x, y, z, u, v, w, ...)
        vector_scatter(x, y, z, f, ...)

    If only 3 arrays u, v, w are passed the x, y and z arrays are assumed to be
    made from the indices of vectors.

    If 4 positional arguments are passed the last one must be a callable, f, 
    that returns vectors.

    **Keyword arguments**:
    
        :name: the name of the vtk object created.

        :scalars: optional scalar data.
       
        :figure: optionally, the figure on which to add the data source."""
    x, y, z, u, v, w = process_regular_vectors(*args)

    scalars = kwargs.pop('scalars', None)
    name = kwargs.pop('name', 'VectorScatter')

    data_source = MGlyphSource()
    data_source.set(x=x, y=y, z=z, u=u, v=v, w=w, scalars=scalars, 
                    trait_change_notify=False)
    data_source.create()

    figure = kwargs.pop('figure', None)
    ds = tools._add_data(data_source.dataset, name, figure=figure)
    data_source.m_data = ds
    return ds


def vector_field(*args, **kwargs):
    """ Creates vector field data. 
    
    **Function signatures**::

        vector_field(u, v, w, ...)
        vector_field(x, y, z, u, v, w, ...)
        vector_field(x, y, z, f, ...)

    If only 3 arrays u, v, w are passed the x, y and z arrays are assumed to be
    made from the indices of vectors.

    If the x, y and z arrays are passed, they should have been generated
    by `numpy.mgrid` or `numpy.ogrid`. The function builds a scalar field
    assuming the points are regularily spaced on an orthogonal grid.

    If 4 positional arguments are passed the last one must be a callable, f, 
    that returns vectors.

    **Keyword arguments**:
        
        :name: the name of the vtk object created.

        :scalars: optional scalar data.
       
        :figure: optionally, the figure on which to add the data source."""
    x, y, z, u, v, w = process_regular_vectors(*args)

    scalars = kwargs.pop('scalars', None)
    data_source = MArraySource()
    data_source.set(x=x, y=y, z=z, u=u, v=v, w=w,
                    scalars = scalars,
                    trait_change_notify=False)
    data_source.create()
    name = kwargs.pop('name', 'VectorField')
    figure = kwargs.pop('figure', None)
    return tools._add_data(data_source.m_data, name, figure=figure)


def scalar_scatter(*args, **kwargs):
    """
    Creates scattered scalar data. 
    
    **Function signatures**::

        scalar_scatter(s, ...)
        scalar_scatter(x, y, z, s, ...)
        scalar_scatter(x, y, z, s, ...)
        scalar_scatter(x, y, z, f, ...)

    If only 1 array s is passed the x, y and z arrays are assumed to be
    made from the indices of vectors.

    If 4 positional arguments are passed the last one must be an array s, or
    a callable, f, that returns an array.

    **Keyword arguments**:
    
        :name: the name of the vtk object created.

        :figure: optionally, the figure on which to add the data source."""
    x, y, z, s = process_regular_scalars(*args)

    if s is not None:
        s = s.ravel()

    data_source = MGlyphSource()
    data_source.set(x=x, y=y, z=z, scalars=s, trait_change_notify=False)
    data_source.create()

    name = kwargs.pop('name', 'ScalarScatter')
    figure = kwargs.pop('figure', None)
    ds = tools._add_data(data_source.dataset, name, figure=figure)
    data_source.m_data = ds
    return ds


def scalar_field(*args, **kwargs):
    """
    Creates a scalar field data.
                      
    **Function signatures**::
    
        scalar_field(s, ...)
        scalar_field(x, y, z, s, ...)
        scalar_field(x, y, z, f, ...)

    If only 1 array s is passed the x, y and z arrays are assumed to be
    made from the indices of arrays.

    If the x, y and z arrays are passed they are supposed to have been
    generated by `numpy.mgrid`. The function builds a scalar field assuming 
    the points are regularily spaced.

    If 4 positional arguments are passed the last one must be an array s, or
    a callable, f, that returns an array.
    
    **Keyword arguments**:

        :name: the name of the vtk object created.

        :figure: optionally, the figure on which to add the data source."""
    x, y, z, s = process_regular_scalars(*args)

    data_source = MArraySource()
    data_source.set(x=x, y=y, z=z,
                    scalars=s,
                    trait_change_notify=False)
    data_source.create()

    name = kwargs.pop('name', 'ScalarField')
    figure = kwargs.pop('figure', None)
    return tools._add_data(data_source.m_data, name, figure=figure)


def line_source(*args, **kwargs):
    """
    Creates line data.
    
    **Function signatures**::
    
        line_source(x, y, z, ...)
        line_source(x, y, z, s, ...)
        line_source(x, y, z, f, ...)

        If 4 positional arguments are passed the last one must be an array s, or
        a callable, f, that returns an array. 

    **Keyword arguments**:
    
        :name: the name of the vtk object created.

        :figure: optionally, the figure on which to add the data source."""
    if len(args)==1:
        raise ValueError, "wrong number of arguments"    
    x, y, z, s = process_regular_scalars(*args)

    data_source = MLineSource()
    data_source.set(x=x, y=y, z=z, scalars=s, trait_change_notify=False)
    data_source.create()

    name = kwargs.pop('name', 'LineSource')
    figure = kwargs.pop('figure', None)
    ds = tools._add_data(data_source.dataset, name, figure=figure)
    data_source.m_data = ds
    return ds


def array2d_source(*args, **kwargs):
    """
    Creates structured 2D data from a 2D array.
    
    **Function signatures**::

        array2d_source(s, ...)
        array2d_source(x, y, s, ...)
        array2d_source(x, y, f, ...)

    If 3 positional arguments are passed the last one must be an array s,
    or a callable, f, that returns an array. x and y give the
    coordinnates of positions corresponding to the s values. 
    
    x and y can be 1D or 2D arrays (such as returned by numpy.ogrid or
    numpy.mgrid), but the points should be located on an orthogonal grid
    (possibly non-uniform). In other words, all the points sharing a same
    index in the s array need to have the same x or y value.

    If only 1 array s is passed the x and y arrays are assumed to be
    made from the indices of arrays, and an uniformly-spaced data set is
    created.

    **Keyword arguments**:
    
        :name: the name of the vtk object created.

        :figure: optionally, the figure on which to add the data source.
        
        :mask: Mask points specified in a boolean masking array.
    """
    data_source = MArray2DSource()
    mask = kwargs.pop('mask', None)
    if len(args) == 1 :
        args = convert_to_arrays(args)
        s = args[0]
        data_source.set(scalars=s, mask=mask, trait_change_notify=False)
    else:
        x, y, s = process_regular_2d_scalars(*args, **kwargs)
        # Do some magic to extract the first row/column, independently of
        # the shape of x and y
        #x = numpy.atleast_2d(x.squeeze().T)[0, :].squeeze()
        #y = numpy.atleast_2d(y.squeeze())[0, :].squeeze()
        data_source.set(x=x, y=y, scalars=s, mask=mask,
                        trait_change_notify=False)

    data_source.create()
    name = kwargs.pop('name', 'Array2DSource')
    figure = kwargs.pop('figure', None)
    return tools._add_data(data_source.m_data, name, figure=figure)


def grid_source(x, y, z, **kwargs):
    """
    Creates 2D grid data.

    x, y, z are 2D arrays giving the positions of the vertices of the surface.
    The connectivity between these points is implied by the connectivity on
    the arrays.
    
    For simple structures (such as orthogonal grids) prefer the array2dsource
    function, as it will create more efficient data structures. 

    **Keyword arguments**:
    
        :name: the name of the vtk object created.
        
        :scalars: optional scalar data.
       
        :figure: optionally, the figure on which to add the data source.
        """
    scalars = kwargs.pop('scalars', None)
    if scalars is None:
        scalars = z

    data_source = MGridSource()
    data_source.set(x=x, y=y, z=z, scalars=scalars,
                    trait_change_notify=False)
    data_source.create()

    name = kwargs.pop('name', 'GridSource')
    figure = kwargs.pop('figure', None)
    ds = tools._add_data(data_source.dataset, name, figure=figure)
    data_source.m_data = ds
    return ds


def open(filename, figure=None):
    """Open a supported data file given a filename.  Returns the source
    object if a suitable reader was found for the file.
    """
    if figure is None:
        engine = tools.get_engine()
    else:
        engine = engine_manager.find_figure_engine(figure)
        engine.current_scene = figure
    src = engine.open(filename)
    return src
    
############################################################################
# Automatically generated sources from registry.
############################################################################
def _create_data_source(metadata):
    """Creates a data source and adds it to the mayavi engine given
    metadata of the source.  Returns the created source.  
    """
    factory = metadata.get_callable()
    src = factory()
    engine = tools.get_engine()
    engine.add_source(src)
    return src

def _make_functions(namespace):
    """Make the automatic functions and add them to the namespace."""
    for src in registry.sources:
        if len(src.extensions) == 0:
            func_name = camel2enthought(src.id)
            if func_name.endswith('_source'):
                func_name = func_name[:-7]
            func = lambda metadata=src: _create_data_source(metadata)
            func.__doc__ = src.help
            func.__name__ = func_name
            # Inject function into the namespace and __all__.
            namespace[func_name] = func
            __all__.append(func_name)

_make_functions(locals())
