"""Repair AaWanWan.ttf: drop the malformed vhea/vmtx (vertical text metrics)
tables that Chrome's OTS sanitizer rejects (vhea version 0x00010001 instead
of the correct 0x00010000). Vertical metrics are unused for our horizontal
engraving text, so removing them is safe and avoids trusting any other
untested field in that same buggy table.

fontTools' save() recomputes the table directory, offsets, padding, and the
head table's checkSumAdjustment automatically, so the result is a clean,
spec-valid sfnt regardless of what else might have been off in the original.
"""
from fontTools.ttLib import TTFont

path = r"c:\Users\Administrator\Downloads\niyan_Laser-main\AaWanWan.ttf"
backup = r"c:\Users\Administrator\Downloads\niyan_Laser-main\AaWanWan.ttf.orig"

import shutil
shutil.copy2(path, backup)

f = TTFont(path)
removed = []
for tag in ('vhea', 'vmtx'):
    if tag in f:
        del f[tag]
        removed.append(tag)
print("removed tables:", removed)
f.save(path)
print("saved:", path)
