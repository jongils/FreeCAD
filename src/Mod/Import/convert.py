# SPDX-License-Identifier: LGPL-2.1-or-later

# ****************************************************************************
# *  FreeCAD STEP 및 IGS/IGES 파일 형식을 위한 3D 모델 변환 유틸리티          *
# *                                                                           *
# *  이 모듈은 STEP(.step/.stp)과 IGS/IGES(.igs/.iges) 형식 사이의            *
# *  3D 모델 변환을 프로그래밍 방식으로 지원하는 헬퍼 함수를 제공합니다.     *
# *                                                                           *
# *  내부 변환 코드 위치:                                                     *
# *    IGES 읽기 : src/Mod/Import/App/ReaderIges.cpp (IGESCAFControl_Reader)  *
# *    IGES 쓰기 : src/Mod/Import/App/WriterIges.cpp (IGESCAFControl_Writer)  *
# *    STEP 읽기 : src/Mod/Import/App/ReaderStep.cpp (STEPCAFControl_Reader)  *
# *    STEP 쓰기 : src/Mod/Import/App/WriterStep.cpp (STEPCAFControl_Writer)  *
# *    Python API : src/Mod/Import/App/AppImportPy.cpp (Import.open/insert/export) *
# ****************************************************************************

"""
STEP 및 IGES 파일 형식 간 3D 모델 변환 유틸리티 모듈.

지원 형식
---------
* STEP : ``.step``, ``.stp``
* IGES : ``.iges``, ``.igs``

사용 예시
---------
STEP 파일을 IGES로 변환::

    import convert
    convert.convert("/경로/모델.step", "/경로/모델.igs")

IGES 파일을 STEP으로 변환::

    import convert
    convert.convert("/경로/모델.igs", "/경로/모델.step")
"""

import os

import FreeCAD
import Import


# ---------------------------------------------------------------------------
# 공개 상수
# ---------------------------------------------------------------------------

#: STEP 형식으로 인식되는 파일 확장자 (소문자, 점 포함).
STEP_EXTENSIONS = frozenset({".step", ".stp"})

#: IGES 형식으로 인식되는 파일 확장자 (소문자, 점 포함).
IGES_EXTENSIONS = frozenset({".iges", ".igs"})

#: 지원되는 모든 파일 확장자.
SUPPORTED_EXTENSIONS = STEP_EXTENSIONS | IGES_EXTENSIONS


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------


def convert(source_file, target_file):
    """STEP 또는 IGES 형식의 3D 모델 파일을 상호 변환합니다.

    *source_file* 을 임시 FreeCAD 문서로 불러온 뒤, 불러온 모든 객체를
    *target_file* 로 내보냅니다. 오류가 발생하더라도 임시 문서는 항상 닫힙니다.

    매개변수
    --------
    source_file : str
        원본 모델 파일 경로. 확장자가 ``.step``, ``.stp``, ``.iges``,
        ``.igs`` 중 하나여야 합니다 (대소문자 구분 없음).
    target_file : str
        변환된 모델을 저장할 경로. 파일 형식은 확장자로 결정됩니다
        (*source_file* 과 동일한 확장자 집합을 지원).

    예외
    ----
    ValueError
        *source_file* 또는 *target_file* 의 확장자가 지원되지 않는 경우.
    RuntimeError
        *source_file* 에서 객체를 읽을 수 없거나, 내부 가져오기/내보내기
        작업이 실패한 경우.

    사용 예
    -------
    STEP 파일을 IGES로 변환:

    >>> import convert
    >>> convert.convert("어셈블리.step", "어셈블리.igs")

    IGES 파일을 STEP으로 변환:

    >>> convert.convert("부품.igs", "부품.step")
    """
    src_ext = os.path.splitext(source_file)[1].lower()
    tgt_ext = os.path.splitext(target_file)[1].lower()

    if src_ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "지원하지 않는 원본 형식 '{}'. 지원 확장자: {}".format(
                src_ext, ", ".join(sorted(SUPPORTED_EXTENSIONS))
            )
        )
    if tgt_ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "지원하지 않는 대상 형식 '{}'. 지원 확장자: {}".format(
                tgt_ext, ", ".join(sorted(SUPPORTED_EXTENSIONS))
            )
        )

    doc = FreeCAD.newDocument("_ImportConversionDoc")
    try:
        Import.insert(source_file, doc.Name)
        objects = list(doc.Objects)
        if not objects:
            raise RuntimeError(
                "'{}' 에서 가져온 객체가 없습니다.".format(source_file)
            )
        Import.export(objects, target_file)
    finally:
        FreeCAD.closeDocument(doc.Name)
