from __future__ import annotations

import math
import struct
import zipfile
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from xml.sax.saxutils import quoteattr

logger = getLogger(__name__)

# Bambu Lab A1 bed. Bambu Studio lays plates out in a grid with a gap of one
# fifth of the bed between them, so objects must sit at these world offsets.
BED_SIZE = 256.0
PLATE_STRIDE = BED_SIZE * 1.2
APPLICATION = "BambuStudio-02.08.02.61"

# Project settings for a Bambu Lab A1 (0.4 mm nozzle, 0.20 mm Standard,
# Bambu PLA Basic), exported by Bambu Studio. Bambu Studio needs the full
# settings to open a multi-plate project.
PROJECT_SETTINGS: Path = Path(__file__).parent / "bambu_a1_project_settings.config"

_XML = '<?xml version="1.0" encoding="UTF-8"?>'
_MODEL_TYPE = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
_MODEL_OPEN = (
    '<model unit="millimeter" xml:lang="en-US"'
    ' xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
    ' xmlns:BambuStudio="http://schemas.bambulab.com/package/2021"'
    ' xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"'
    ' requiredextensions="p">'
)
_CONTENT_TYPES = "\n".join(
    [
        _XML,
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        ' <Default Extension="rels"'
        ' ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        ' <Default Extension="model"'
        ' ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>',
        ' <Default Extension="png" ContentType="image/png"/>',
        "</Types>",
        "",
    ]
)
_RELS_OPEN = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'


@dataclass(frozen=True)
class Mesh:
    """Indexed triangle mesh."""

    vertices: list[tuple[float, float, float]]
    triangles: list[tuple[int, int, int]]


def read_stl(path: Path) -> Mesh:
    """
    Read an ASCII or binary STL file into an indexed mesh.

    Shared corners are merged, so the mesh is suitable for a 3MF file.

    Args:
        path: STL file to read.

    Returns:
        The indexed mesh.
    """
    data = path.read_bytes()
    corners = _ascii_corners(data) if data.lstrip().startswith(b"solid") else []
    if not corners:
        corners = _binary_corners(data)
    index: dict[tuple[float, float, float], int] = {}
    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []
    for i in range(0, len(corners), 3):
        ids = []
        for corner in corners[i : i + 3]:
            if corner not in index:
                index[corner] = len(vertices)
                vertices.append(corner)
            ids.append(index[corner])
        if len(set(ids)) == 3:
            triangles.append((ids[0], ids[1], ids[2]))
    return Mesh(vertices, triangles)


def _ascii_corners(data: bytes) -> list[tuple[float, float, float]]:
    corners = []
    for line in data.decode("ascii", errors="ignore").splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] == "vertex":
            corners.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return corners


def _binary_corners(data: bytes) -> list[tuple[float, float, float]]:
    (count,) = struct.unpack_from("<I", data, 80)
    corners = []
    for t in range(count):
        values = struct.unpack_from("<12f", data, 84 + t * 50)
        corners += [tuple(values[3 + 3 * k : 6 + 3 * k]) for k in range(3)]
    return corners


def centred(mesh: Mesh) -> Mesh:
    """
    Move a mesh so its footprint is centred on the origin and it rests on z = 0.

    Args:
        mesh: Mesh to move.

    Returns:
        The moved mesh.
    """
    lo = [min(v[i] for v in mesh.vertices) for i in range(3)]
    hi = [max(v[i] for v in mesh.vertices) for i in range(3)]
    shift = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2])
    vertices = [(x - shift[0], y - shift[1], z - shift[2]) for x, y, z in mesh.vertices]
    return Mesh(vertices, mesh.triangles)


def plate_origin(index: int, count: int) -> tuple[float, float]:
    """
    World position of the front-left corner of a plate, as Bambu Studio lays them out.

    Args:
        index: Plate index, starting at 0.
        count: Total number of plates.

    Returns:
        The (x, y) offset of the plate.
    """
    root = math.sqrt(count)
    cols = round(root) + (1 if root > round(root) else 0)
    return (index % cols) * PLATE_STRIDE, -(index // cols) * PLATE_STRIDE


def _object_model(object_id: int, mesh: Mesh) -> str:
    lines = [_XML, _MODEL_OPEN, " <resources>", f'  <object id="{object_id}" type="model">']
    lines += ["   <mesh>", "    <vertices>"]
    lines += [f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in mesh.vertices]
    lines += ["    </vertices>", "    <triangles>"]
    lines += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.triangles]
    lines += ["    </triangles>", "   </mesh>", "  </object>", " </resources>", " <build/>"]
    lines += ["</model>", ""]
    return "\n".join(lines)


def _main_model(names: list[str]) -> str:
    lines = [_XML, _MODEL_OPEN, f' <metadata name="Application">{APPLICATION}</metadata>']
    lines += [' <metadata name="BambuStudio:3mfVersion">1</metadata>', " <resources>"]
    for k in range(len(names)):
        lines += [
            f'  <object id="{2 * k + 2}" type="model">',
            "   <components>",
            f'    <component p:path="/3D/Objects/object_{k + 1}.model"'
            f' objectid="{2 * k + 1}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>',
            "   </components>",
            "  </object>",
        ]
    lines += [" </resources>", " <build>"]
    for k in range(len(names)):
        x, y = plate_origin(k, len(names))
        lines.append(
            f'  <item objectid="{2 * k + 2}" transform="1 0 0 0 1 0 0 0 1'
            f' {x + BED_SIZE / 2:.4f} {y + BED_SIZE / 2:.4f} 0" printable="1"/>'
        )
    lines += [" </build>", "</model>", ""]
    return "\n".join(lines)


def _model_settings(names: list[str], overrides: dict[str, str]) -> str:
    lines = [_XML, "<config>"]
    for k, name in enumerate(names):
        label = quoteattr(name)
        lines += [
            f'  <object id="{2 * k + 2}">',
            f'    <metadata key="name" value={label}/>',
            '    <metadata key="extruder" value="1"/>',
        ]
        lines += [
            f'    <metadata key="{key}" value={quoteattr(v)}/>' for key, v in overrides.items()
        ]
        lines += [
            f'    <part id="{2 * k + 1}" subtype="normal_part">',
            f'      <metadata key="name" value={label}/>',
            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
            "    </part>",
            "  </object>",
        ]
    for k, name in enumerate(names):
        lines += [
            "  <plate>",
            f'    <metadata key="plater_id" value="{k + 1}"/>',
            f'    <metadata key="plater_name" value={quoteattr(name)}/>',
            '    <metadata key="locked" value="false"/>',
            "    <model_instance>",
            f'      <metadata key="object_id" value="{2 * k + 2}"/>',
            '      <metadata key="instance_id" value="0"/>',
            f'      <metadata key="identify_id" value="{100 + k}"/>',
            "    </model_instance>",
            "  </plate>",
        ]
    lines += ["</config>", ""]
    return "\n".join(lines)


def _rels(targets: list[str]) -> str:
    lines = [_XML, _RELS_OPEN]
    lines += [
        f' <Relationship Target="{target}" Id="rel-{k + 1}" Type="{_MODEL_TYPE}"/>'
        for k, target in enumerate(targets)
    ]
    lines += ["</Relationships>", ""]
    return "\n".join(lines)


def write_project(stls: list[Path], output: Path, overrides: dict[str, str] | None = None) -> Path:
    """
    Write a Bambu Studio project for a Bambu Lab A1 with one STL per plate.

    Each part is centred on its own plate and the plate is named after the
    file, so the project opens ready to slice plate by plate.

    Args:
        stls: STL files, one plate each, in plate order.
        output: Path of the ``.3mf`` project to write.
        overrides: Print settings applied to every object, e.g.
            ``{"sparse_infill_density": "100%"}``.

    Returns:
        Path of the written project.
    """
    names = [path.stem for path in stls]
    objects = [f"/3D/Objects/object_{k + 1}.model" for k in range(len(stls))]
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES)
        zf.writestr("_rels/.rels", _rels(["/3D/3dmodel.model"]))
        zf.writestr("3D/_rels/3dmodel.model.rels", _rels(objects))
        zf.writestr("3D/3dmodel.model", _main_model(names))
        for k, path in enumerate(stls):
            mesh = centred(read_stl(path))
            zf.writestr(objects[k].lstrip("/"), _object_model(2 * k + 1, mesh))
        zf.writestr("Metadata/model_settings.config", _model_settings(names, overrides or {}))
        zf.write(PROJECT_SETTINGS, "Metadata/project_settings.config")
    logger.info("Wrote %s (%d plates)", output, len(stls))
    return output
