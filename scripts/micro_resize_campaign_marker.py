from pathlib import Path

index = Path('index.html')
source_test = Path('tests/source-smoke.spec.js')
smoke_test = Path('tests/smoke.spec.js')

s = index.read_text()
repls = [
    ('iconSize: [52, 74],', 'iconSize: [46, 66],'),
    ('iconAnchor: [26, 74],', 'iconAnchor: [23, 66],'),
    ('popupAnchor: [0, -72],', 'popupAnchor: [0, -64],'),
]
for old, new in repls:
    if s.count(old) != 1:
        raise SystemExit(f'Expected exactly one occurrence of {old!r}, found {s.count(old)}')
    s = s.replace(old, new, 1)
index.write_text(s)

s = source_test.read_text()
for old, new in [
    ("expect(indexSource).toContain('iconSize: [52, 74]');", "expect(indexSource).toContain('iconSize: [46, 66]');"),
    ("expect(indexSource).toContain('iconAnchor: [26, 74]');", "expect(indexSource).toContain('iconAnchor: [23, 66]');"),
]:
    if s.count(old) != 1:
        raise SystemExit(f'Source smoke anchor mismatch for {old!r}: {s.count(old)}')
    s = s.replace(old, new, 1)
source_test.write_text(s)

s = smoke_test.read_text()
for old, new in [
    ('expect(marker.activeSize).toEqual([52, 74]);', 'expect(marker.activeSize).toEqual([46, 66]);'),
    ('expect(marker.activeAnchor).toEqual([26, 74]);', 'expect(marker.activeAnchor).toEqual([23, 66]);'),
]:
    if s.count(old) != 1:
        raise SystemExit(f'Live smoke anchor mismatch for {old!r}: {s.count(old)}')
    s = s.replace(old, new, 1)
smoke_test.write_text(s)

print('Campaign marker display resized 52x74 -> 46x66; anchor 26,74 -> 23,66.')
