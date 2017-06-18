"""
`uidoc.Selection` Wrapper
"""

import rpw
from rpw.revit import revit, DB, UI
from rpw.utils.dotnet import List
from rpw.base import BaseObjectWrapper, BaseObject
from rpw.exceptions import RpwTypeError
from rpw.utils.logger import logger
from rpw.utils.coerce import to_element_ids, to_elements, to_iterable
from rpw.db.collections_ import ElementSet

ObjectType = UI.Selection.ObjectType
PickObjects = revit.uidoc.Selection.PickObjects
PickObject = revit.uidoc.Selection.PickObject

class Selection(BaseObjectWrapper, ElementSet):
    """
    >>> selection = rpw.ui.Selection()
    >>> selection[0]
    FirstElement
    >>> selection.element_ids
    [ SomeElementId, SomeElementId, ...]
    >>> selection.elements
    [ SomeElement, SomeElement, ...]
    >>> len(selection)
    2

    Wrapped Element:
        _revit_object = `Revit.UI.Selection`
    """

    _revit_object_class = UI.Selection.Selection

    def __init__(self, elements_or_ids=None, uidoc=revit.uidoc):
        """
        Initializes Selection. Elements or ElementIds are optional.
        If no elements are provided on intiialization,
        selection handler will be created with selected elements.

        Args:
            elements ([DB.Element or DB.ElementID]): Elements or ElementIds

        >>> selection = Selection(SomeElement)
        >>> selection = Selection(SomeElementId)
        >>> selection = Selection([Element, Element, Element, ...])

        """

        BaseObjectWrapper.__init__(self, uidoc.Selection)
        self.uidoc = uidoc

        if not elements_or_ids:
            # Is List of elements is not provided, uses uidoc selection
            elements_or_ids = [e for e in uidoc.Selection.GetElementIds()]

        ElementSet.__init__(self, elements_or_ids, doc=self.uidoc.Document)

    def add(self, elements_or_ids):
        """ Adds elements to selection.

        Args:
            elements ([DB.Element or DB.ElementID]): Elements or ElementIds

        >>> selection = Selection()
        >>> selection.add(SomeElement)
        >>> selection.add([elements])
        >>> selection.add([element_ids])
        """
        # Call Set for proper adding into set.
        ElementSet.add(self, elements_or_ids)
        self.update()

    # def update(self):
    #     """ Updates Selection() object to match current selection state"""
    #     Selection.__init__(self, uidoc=self.uidoc)

    def update(self):
        """ Forces UI selection to match the Selection() object """
        self.uidoc.Selection.SetElementIds(self.as_element_id_list())

    def clear(self):
        """ Clears Selection

        >>> selection = Selection()
        >>> selection.clear()

        Returns:
            None
        """
        ElementSet.clear(self)
        self.update()

    def __bool__(self):
        """
        Returns:
            bool: `False` if selection  is empty, `True` otherwise

        >>> len(selection)
        2
        >>> Selection() is True
        True
        """
        return bool(len(self))

    def __repr__(self):
        """ Adds data to Base __repr__ to add selection count"""
        return super(Selection, self).__repr__(data={'count': len(self)})


    def _pick(self, obj_type, msg='', multiple=False):
        """ Note: Moved Reference Logic to Referenc Wrapper."""
        doc = self.uidoc.Document

        if multiple:
            references = PickObjects(obj_type, msg)
        else:
            references = PickObject(obj_type, msg)

        self.add(references)
        return references


    def pick_element(self, msg='', multiple=False):
        return self._pick(ObjectType.Element, msg=msg, multiple=multiple)

    def pick_pt_on_element(self, msg='', multiple=False):
        return self._pick(ObjectType.PointOnElement, msg=msg, multiple=multiple)

    def pick_pt(self, msg=''):
        """ This does not add eleents to selection """
        return self.uidoc.Selection.PickPoint(msg)

    def pick_edge(self, msg='', multiple=False):
        return self._pick(ObjectType.Edge, msg=msg, multiple=multiple)

    def pick_face(self, msg='', multiple=False):
        return self._pick(ObjectType.Face, msg=msg, multiple=multiple)

    def pick_linked_element(self, msg='', multiple=False):
        return self._pick(ObjectType.LinkedElement, msg=msg, multiple=multiple)
