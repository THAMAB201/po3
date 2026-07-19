from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "PO3_MMXM_Enigma_Core.pine"
REPORT = ROOT / "enigma_build" / "build_report.txt"

source = CORE.read_text(encoding="utf-8")

replacements = [
    (
        'text="NY SESSION  |  LIVE\nNET  0.00 PTS  •  0 TRADES"',
        'text="NY SESSION  |  LIVE\\nNET  0.00 PTS  •  0 TRADES"',
    ),
    (
        'string resultLabelText = "NY SESSION  |  " + resultStatus + "\nNET  " + signedPointsText(displayedSessionPoints)',
        'string resultLabelText = "NY SESSION  |  " + resultStatus + "\\nNET  " + signedPointsText(displayedSessionPoints)',
    ),
]

for old, new in replacements:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one generated newline pattern, found {count}: {old!r}")
    source = source.replace(old, new, 1)

if 'text="NY SESSION  |  LIVE\nNET' in source:
    raise RuntimeError("Creation label still contains a physical newline inside its Pine string")
if 'resultStatus + "\nNET' in source:
    raise RuntimeError("Result label update still contains a physical newline inside its Pine string")
if 'text="NY SESSION  |  LIVE\\nNET' not in source:
    raise RuntimeError("Escaped creation-label newline is missing")
if 'resultStatus + "\\nNET' not in source:
    raise RuntimeError("Escaped result-label newline is missing")

CORE.write_text(source, encoding="utf-8")

report_lines = REPORT.read_text(encoding="utf-8").splitlines()
report_lines = [line for line in report_lines if not line.startswith("core_lines=") and not line.startswith("pine_string_newlines=")]
report_lines.insert(1, f"core_lines={len(source.splitlines())}")
report_lines.append("pine_string_newlines=escaped")
REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

print(f"fixed_core_lines={len(source.splitlines())}")
