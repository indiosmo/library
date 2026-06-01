---
source: https://www.youtube.com/watch?v=IroPQ150F6c
type: video
file: "[[Andrew Kelley- A Practical Guide to Applying Data Oriented Design (DoD).webm]]"
tags:
  - data-oriented-design
  - zig
  - andrew-kelley
  - performance
  - cpu-cache
  - compilers
  - memory-layout
---

## Description

Copyright: Belongs to Handmade Seattle (https ://vimeo.com/649009599). I'm not the owner of the video and hold no copyright.  And the video is not monetized.

In this video Andrew Kelley (creator of Zig programming language) explains various strategies one can use to reduce memory footprint of programs while also making the program cache friendly which increase throughput.

At the end he presents a case study where DoD principles are used in Zig compiler for faster compilation.

References:

- CppCon 2014: Mike Acton "Data-Oriented Design and C++": youtube.com/watch?v=rX0ItVEVjHc
- Handmade Seattle: handmade-seattle.com/
- Richard Fabian, 'Data-Oriented Design': dataorienteddesign.com/dodbook/
- IT Hare, 'Infographics: Operation Costs in CPU Clock Cycles': ithare.com/infographics-operation-costs-in-cpu-clock-cycles/
- The Brain Dump, 'Handles are the better pointers': floooh.github.io/2018/06/17/handles-vs-pointers.html

## Auto Summary

Andrew Kelley delivered this talk at Handmade Seattle 2021, an independent conference for systems programmers covering game engines, operating systems, and compilers. He frames it as picking up where Mike Acton's 2014 CppCon talk "Data-Oriented Design and C++" left off, translating those ideas into concrete techniques: struct field reordering, shrinking data types, encoding state in handles rather than pointers, and segregating hot from cold data. The closing case study draws on his real work shrinking the Zig compiler's in-memory representation to speed up compilation.

