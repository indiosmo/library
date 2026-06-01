---
source: https://www.youtube.com/watch?v=PBQN62oUnN8
type: video
file: "[[Brandon Rhodes- Hoist Your I⧸O - PyWaw Summit 2015.mkv]]"
tags:
  - python
  - software-architecture
  - brandon-rhodes
  - functional-core-imperative-shell
  - decoupling
  - testing
  - lecture
---

## Description

Talk: Hoist Your I/O

Our programs too often leave control decisions stranded in low-level routines, producing tightly coupled systems that make it difficult to re-use code. What are the warning signs of tightly coupled I/O and how can it be corrected? Particular attention will be paid to the way that modern Python syntax supports a broader array of solutions than were once possible!

Speaker: Brandon Rhodes. Brandon is a programmer and instructor working at Dropbox, and is excited that this is his third chance to speak at a Python event in Poland.  For 17 years Brandon has maintained the most popular amateur astronomy library for Python, and will be the Chair of PyCon 2016–2017 in Portland, Oregon.

Slides: http://rhodesmill.org/brandon/slides/2015-05-pywaw/hoist/

License: For reuse of this video under a more permissive license please get in touch with us. The speakers retain the copyright for their performances.

http://summit.pywaw.org

## Auto Summary

Brandon Rhodes is best known in the Python world for his astronomy libraries PyEphem and its successor Skyfield, and for talks on software design and clean architecture. "Hoist Your I/O" reframes the "functional core, imperative shell" idea (popularized by Gary Bernhardt): push side effects like file and network access up to the edges of a program so a pure, easily testable decision-making core sits underneath, instead of stranding I/O deep in the call stack where it tightly couples logic to its environment. The chapters trace this through a worked file-reading example, data structures, generators, database facades, and a critique of the classic Gang of Four design patterns as workarounds for limitations that Python's dynamic features make unnecessary. PyWaw Summit was a conference run by the Warsaw Python user group (PyWaw).

