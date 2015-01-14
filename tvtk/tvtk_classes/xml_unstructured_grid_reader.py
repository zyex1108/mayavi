# Automatically generated code: EDIT AT YOUR OWN RISK
from traits import api as traits
from traitsui import api as traitsui

from tvtk import vtk_module as vtk
from tvtk import tvtk_base
from tvtk.tvtk_base_handler import TVTKBaseHandler
from tvtk import messenger
from tvtk.tvtk_base import deref_vtk
from tvtk import array_handler
from tvtk.array_handler import deref_array
from tvtk.tvtk_classes.tvtk_helper import wrap_vtk

from tvtk.tvtk_classes.xml_unstructured_data_reader import XMLUnstructuredDataReader


class XMLUnstructuredGridReader(XMLUnstructuredDataReader):
    """
    XMLUnstructuredGridReader - Read VTK XML unstructured_grid files.
    
    Superclass: XMLUnstructuredDataReader
    
    XMLUnstructuredGridReader reads the VTK XML unstructured_grid file
    format.  One unstructured grid file can be read to produce one
    output.  Streaming is supported.  The standard extension for this
    reader's file format is "vtu".  This reader is also used to read a
    single piece of the parallel file format.
    
    See Also:
    
    XMLPUnstructuredGridReader
    
    """
    def __init__(self, obj=None, update=True, **traits):
        tvtk_base.TVTKBase.__init__(self, vtk.vtkXMLUnstructuredGridReader, obj, update, **traits)
    
    def _get_output(self):
        return wrap_vtk(self._vtk_obj.GetOutput())
    output = traits.Property(_get_output,
                             help="Output of this source, i.e. the result of `get_output()`.")
    
    def get_output(self, idx=None):
        """
        V.get_output() -> UnstructuredGrid
        C++: UnstructuredGrid *GetOutput()
        V.get_output(int) -> UnstructuredGrid
        C++: UnstructuredGrid *GetOutput(int idx)
        Get the reader's output.
        """
        if idx is None:
            return wrap_vtk(self._vtk_obj.GetOutput())
        else:
            return wrap_vtk(self._vtk_obj.GetOutput(idx))

    _updateable_traits_ = \
    (('time_step_range', 'GetTimeStepRange'), ('abort_execute',
    'GetAbortExecute'), ('progress', 'GetProgress'), ('release_data_flag',
    'GetReleaseDataFlag'), ('time_step', 'GetTimeStep'),
    ('reference_count', 'GetReferenceCount'), ('file_name',
    'GetFileName'), ('progress_text', 'GetProgressText'), ('debug',
    'GetDebug'), ('global_warning_display', 'GetGlobalWarningDisplay'))
    
    _full_traitnames_list_ = \
    (['abort_execute', 'debug', 'global_warning_display',
    'release_data_flag', 'file_name', 'progress_text', 'time_step',
    'time_step_range'])
    
    def trait_view(self, name=None, view_element=None):
        if view_element is not None or name not in (None, '', 'traits_view', 'full_traits_view', 'view'):
            return super(XMLUnstructuredGridReader, self).trait_view(name, view_element)
        if name == 'full_traits_view':
            full_traits_view = \
            traitsui.View((traitsui.Item("handler._full_traits_list",show_label=False)),
            title='Edit XMLUnstructuredGridReader properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return full_traits_view
        elif name == 'view':
            view = \
            traitsui.View(([], [], ['file_name', 'time_step', 'time_step_range']),
            title='Edit XMLUnstructuredGridReader properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return view
        elif name in (None, 'traits_view'):
            traits_view = \
            traitsui.View((traitsui.HGroup(traitsui.spring, "handler.view_type", show_border=True), 
            traitsui.Item("handler.info.object", editor = traitsui.InstanceEditor(view_name="handler.view"), style = "custom", show_label=False)),
            title='Edit XMLUnstructuredGridReader properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return traits_view
            
