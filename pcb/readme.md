# Robot PCB

These are the KiCad files for the robots.

# BODGES!

Of course, these did not work on the first try and because of time constraints a second revision could not be made. The built robots therefore implement bodges to fix two issues:

1. The BST and SW pins are swapped because of inconsistencies between the KiCad symbol and datasheet. Fixing involves tombstoning L1 onto the top pad and dragging a bodge wire from the other side of L1 to the right pad of C4.
2. Some of the bumpers are routed to input-only ESP32 pins. This is fixed by dragging bodge wires between these pins and available IO pins, and adjusting the firmware accordingly. See `hardware.py` in the firmware folder for pin mappings.

These issues are not fixed in the provided kicad files.
