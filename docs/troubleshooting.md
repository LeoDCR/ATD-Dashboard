This document is about all the issues that came up and how they were solved

V 1.2:

- Overlapping text on speed gauge: There is a bug where a smaller number (like '52') shows up behind the actual speed number on the main gauge. It's probably an extra Text element I forgot to remove or a weird anchoring issue in the QML. Needs to be fixed in the next versions.