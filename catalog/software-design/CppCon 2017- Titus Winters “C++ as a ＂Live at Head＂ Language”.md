---
source: https://www.youtube.com/watch?v=tISy7EJQPzI
type: video
file: "[[CppCon 2017- Titus Winters “C++ as a ＂Live at Head＂ Language”.mkv]]"
tags:
  - c++
  - software-engineering
  - dependency-management
  - semantic-versioning
  - abseil
  - google
  - api-design
---

## Description

http://CppCon.org
—
Presentation Slides, PDFs, Source Code and other presenter materials are available at: https://github.com/CppCon/CppCon2017
—
Engineering is programming integrated over time. That is to say, as much as it can be difficult to get your code to build and run correctly, it is manifestly harder to keep it working in the face of changing assumptions and requirements. This is true no matter the scale, from a small program to a shared library. Only two solutions have been shown to be theoretically sound: never change or provide no compatibility guarantees. What if there were a third option? What if we took the question of maintenance out of the realm of theory and moved it to practice? This talk discusses the approach we've used at Google and how that intersects with other languages, package management, API and ABI compatibility, and a host of other software engineering practices. The particulars of C++ as a language and an ecosystem make it well positioned for a different approach: Live at Head.
— 
Titus Winters: Google, C++ Codebase Cultivator, NYC

Titus Winters has spent the past 6 years working on Google's core C++ libraries. He's particularly interested in issues of large scale software engineer and codebase maintenance: how do we keep a codebase of over 100M lines of code consistent and flexible for the next decade? Along the way he has helped Google teams pioneer techniques to perform automated code transformations on a massive scale, and helps maintain the Google C++ Style Guide.
—
Videos Filmed & Edited by Bash Films: http://www.BashFilms.com 

Work at Hudson River Trading (HRT): https://tinyurl.com/safxfctf
---

Videos Filmed & Edited by Bash Films: http://www.BashFilms.com

## Auto Summary

Titus Winters chaired the C++ standards committee's library evolution working group (LEWG) and led Google's foundational C++ libraries team; the "Live at Head" philosophy he argues here was later expanded into the 2020 O'Reilly book Software Engineering at Google, which he co-edited. The talk doubles as the public introduction to Abseil, Google's open-source C++ common libraries, which were released on GitHub in September 2017 around the same time as this CppCon. The argument connects to Hyrum's Law (the observation, named after Winters' colleague Hyrum Wright, that all observable behaviors of an interface will eventually be depended upon) and to Google's large-scale automated refactoring tooling that makes continuous upgrades across 100M+ lines feasible.

