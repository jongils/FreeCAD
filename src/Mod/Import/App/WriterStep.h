// SPDX-License-Identifier: LGPL-2.1-or-later

/***************************************************************************
 *   Copyright (c) 2023 Werner Mayer <wmayer[at]users.sourceforge.net>     *
 *                                                                         *
 *   This file is part of FreeCAD.                                         *
 *                                                                         *
 *   FreeCAD is free software: you can redistribute it and/or modify it    *
 *   under the terms of the GNU Lesser General Public License as           *
 *   published by the Free Software Foundation, either version 2.1 of the  *
 *   License, or (at your option) any later version.                       *
 *                                                                         *
 *   FreeCAD is distributed in the hope that it will be useful, but        *
 *   WITHOUT ANY WARRANTY; without even the implied warranty of            *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU      *
 *   Lesser General Public License for more details.                       *
 *                                                                         *
 *   You should have received a copy of the GNU Lesser General Public      *
 *   License along with FreeCAD. If not, see                               *
 *   <https://www.gnu.org/licenses/>.                                      *
 *                                                                         *
 **************************************************************************/

#pragma once

#include <Mod/Import/ImportGlobal.h>
#include <Base/FileInfo.h>
#include <TDocStd_Document.hxx>

namespace Import
{

/**
 * STEP 파일 출력 클래스.
 *
 * ## 입력 데이터 형태
 * write() 메서드는 `Handle(TDocStd_Document)` — OpenCASCADE XCAF 문서 핸들을 받습니다.
 * 이 문서는 XCAF(Extended CAF) 구조로, 형상(Shape)·색상(Color)·이름(Name) 등의
 * 메타데이터를 트리 형태로 보관합니다.
 *
 * ## 데이터 공급 함수
 * 호출 측(AppImportPy.cpp의 exporter())이 다음 순서로 문서를 생성하여 전달합니다:
 *
 *   1. `XCAFApp_Application::GetApplication()->NewDocument("MDTV-CAF", hDoc)`
 *      — 빈 XCAF 문서 생성
 *   2. `ExportOCAF2::exportObjects(objs)` (또는 레거시 `ExportOCAFCmd::exportObjects`)
 *      — FreeCAD `App::DocumentObject*` 목록을 XCAF 문서로 변환
 *      (TopoShape → XCAFDoc_ShapeTool, 색상 → XCAFDoc_ColorTool)
 *   3. `WriterStep::write(hDoc)`
 *      — 완성된 문서를 STEPCAFControl_Writer로 STEP 파일에 씁니다
 *
 * ## 내부 동작
 * - `STEPCAFControl_Writer::Transfer(hDoc, STEPControl_AsIs)` 로 XCAF 문서를 STEP 엔터티로 변환
 * - 헤더(Author/Company/OriginatingSystem)는 BaseApp/Preferences/Mod/Part/STEP 설정에서 읽습니다
 * - STEP은 UTF-8을 지원하지 않으므로 FileName 필드는 헤더에 포함하지 않습니다
 *   (참고: https://forum.freecad.org/viewtopic.php?f=8&t=52967)
 * - `writer.Write(filename)` 로 파일 저장; 실패 시 Base::FileException 발생
 */
class ImportExport WriterStep
{
public:
    /// @param file 출력 STEP 파일 경로 (Base::FileInfo 래퍼)
    explicit WriterStep(const Base::FileInfo& file);

    /**
     * XCAF 문서를 STEP 형식으로 파일에 씁니다.
     *
     * @param hDoc  ExportOCAF2::exportObjects() 가 채운 TDocStd_Document 핸들.
     *              문서 안의 형상·색상 정보가 STEP 엔터티로 변환됩니다.
     * @throws Base::FileException  파일을 열거나 쓸 수 없을 때
     */
    void write(Handle(TDocStd_Document) hDoc) const;

private:
    Base::FileInfo file;
};
}  // namespace Import
