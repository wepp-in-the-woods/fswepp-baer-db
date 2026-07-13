#!/usr/bin/env python3
"""Convert the Access-style XML exports in the repository root to compact JSON.

Values intentionally remain strings: the source XML does not encode types and
this prevents loss of precision or changes to identifiers and dates.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = {
    "Projects.xml": ("Projects", "projects.json"),
    "Treatment Costs.xml": ("Treatment_x0020_Costs", "treatment-costs.json"),
    "Treatments.xml": ("Treatments", "treatments.json"),
}


def json_name(xml_name: str) -> str:
    """Return a browser-friendly name from an XML/Access column name."""
    return re.sub(r"_x([0-9A-Fa-f]{4})_", lambda m: chr(int(m[1], 16)), xml_name)


def main() -> None:
    for source_name, (record_tag, output_name) in EXPORTS.items():
        source = ROOT / source_name
        root = ET.parse(source).getroot()
        records = []
        for record in root.findall(record_tag):
            records.append(
                {json_name(field.tag): field.text or "" for field in record}
            )

        payload = {
            "generated": root.attrib.get("generated"),
            "records": records,
        }
        output = ROOT / output_name
        output.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        print(f"{source.name}: {len(records):,} records -> {output.name}")


if __name__ == "__main__":
    main()
