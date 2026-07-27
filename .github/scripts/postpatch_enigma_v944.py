from pathlib import Path

path = Path('enigma/PO3_MMXM_Enigma_Strategy_V9_4_4_Dynamic_30m_Narrative.pine')
text = path.read_text(encoding='utf-8')

old = '''        bool foundationFrozen = targetFoundation.active and targetFoundation.status == market.STATUS_CONFIRMED
        bool acceptedFoundation = not foundationFrozen and armMoreExtreme(targetFoundation, combinedSeed, fpiEvent.direction)
'''
new = '''        // Keep searching the active interval for the true extreme. A confirmed
        // but less-extreme foundation may be replaced before the window resolves.
        // Once an entry completes, the window is sealed.
        bool acceptedFoundation = not windowResolved and armMoreExtreme(targetFoundation, combinedSeed, fpiEvent.direction)
'''
if old not in text:
    raise RuntimeError('foundation freeze anchor not found')
text = text.replace(old, new, 1)

text = text.replace(
    '// Bind both possibilities. The same displacement that validated the foundation\n// can create the IMB; the entry still waits for a later retest/close.',
    '// Bind only a same-direction IMB created by the confirming displacement or later.\n// Entry still waits for its later retest and directional close.',
    1,
)

text = text.replace(
    '        opposingJudasImb = judasDirection == market.DIR_LONG ? bearImbCandidate : bullImbCandidate\n',
    '',
    1,
)

required = [
    'bool acceptedFoundation = not windowResolved and armMoreExtreme',
    'true extreme',
    'Bind only a same-direction IMB',
]
for marker in required:
    if marker not in text:
        raise RuntimeError(f'missing postpatch marker: {marker}')

path.write_text(text, encoding='utf-8')
