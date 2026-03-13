# SPDX-License-Identifier: LGPL-2.1-or-later

# ****************************************************************************
# *  FreeCAD model conversion utility for STEP and IGS/IGES file formats     *
# *                                                                           *
# *  This module provides helper functions to convert 3D models between      *
# *  STEP (.step/.stp) and IGS/IGES (.igs/.iges) formats programmatically.  *
# *                                                                           *
# *  Underlying conversion code:                                             *
# *    IGES reader : src/Mod/Import/App/ReaderIges.cpp  (IGESCAFControl_Reader) *
# *    IGES writer : src/Mod/Import/App/WriterIges.cpp  (IGESCAFControl_Writer) *
# *    STEP reader : src/Mod/Import/App/ReaderStep.cpp  (STEPCAFControl_Reader) *
# *    STEP writer : src/Mod/Import/App/WriterStep.cpp  (STEPCAFControl_Writer) *
# *    Python API  : src/Mod/Import/App/AppImportPy.cpp (Import.open/insert/export) *
# ****************************************************************************

"""
Utility module for converting 3D model files between STEP and IGES formats.

Supported formats
-----------------
* STEP : ``.step``, ``.stp``
* IGES : ``.iges``, ``.igs``

Typical usage
-------------
Convert a STEP file to IGES::

    import convert
    convert.convert("/path/to/model.step", "/path/to/model.igs")

Convert an IGES file to STEP::

    import convert
    convert.convert("/path/to/model.igs", "/path/to/model.step")
"""

import os

import FreeCAD
import Import


# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

#: File extensions recognised as STEP format (lower-case, with leading dot).
STEP_EXTENSIONS = frozenset({".step", ".stp"})

#: File extensions recognised as IGES format (lower-case, with leading dot).
IGES_EXTENSIONS = frozenset({".iges", ".igs"})

#: All supported file extensions.
SUPPORTED_EXTENSIONS = STEP_EXTENSIONS | IGES_EXTENSIONS


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def convert(source_file, target_file):
    """Convert a 3D model file between STEP and IGES formats.

    The function imports *source_file* into a temporary FreeCAD document and
    immediately exports all resulting objects to *target_file*.  The temporary
    document is always closed afterwards, even if an error occurs.

    Parameters
    ----------
    source_file : str
        Path to the source model file.  Must have a ``.step``, ``.stp``,
        ``.iges``, or ``.igs`` extension (case-insensitive).
    target_file : str
        Destination path for the converted model.  The format is determined
        by the file extension (same set as *source_file*).

    Raises
    ------
    ValueError
        If *source_file* or *target_file* has an unsupported extension.
    RuntimeError
        If no objects could be read from *source_file*, or if the underlying
        import/export operation fails.

    Examples
    --------
    Convert a STEP file to IGES:

    >>> import convert
    >>> convert.convert("assembly.step", "assembly.igs")

    Convert an IGES file to STEP:

    >>> convert.convert("part.igs", "part.step")
    """
    src_ext = os.path.splitext(source_file)[1].lower()
    tgt_ext = os.path.splitext(target_file)[1].lower()

    if src_ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported source format '{}'. Supported extensions: {}".format(
                src_ext, ", ".join(sorted(SUPPORTED_EXTENSIONS))
            )
        )
    if tgt_ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported target format '{}'. Supported extensions: {}".format(
                tgt_ext, ", ".join(sorted(SUPPORTED_EXTENSIONS))
            )
        )

    doc = FreeCAD.newDocument("_ImportConversionDoc")
    try:
        Import.insert(source_file, doc.Name)
        objects = list(doc.Objects)
        if not objects:
            raise RuntimeError(
                "No objects were imported from '{}'.".format(source_file)
            )
        Import.export(objects, target_file)
    finally:
        FreeCAD.closeDocument(doc.Name)
