---
source: https://www.youtube.com/watch?v=DKLzboO2hwc
type: video
file: "[[Declarative Style Evolved - Declarative Structure - Ben Deane - C++Now 2025.webm]]"
tags:
  - cpp
  - functional-programming
  - software-architecture
  - zero-cost-abstraction
  - ben-deane
  - conference-talk
  - api-design
---

## Description

https://www.cppnow.org
---

Declarative Style Evolved - Declarative Structure - Ben Deane - C++Now 2025
---

• If it compiles, it should be correct.
• It should be easy to use and change.
• It should run fast enough.
• It should be testable.

I'm sure we could all extend this wish list indefinitely with desirable properties of code. The question is, how to do we apply this beyond small areas of local concern?

How can we deal with the complexities of common cross-cutting concerns like IO, networking, concurrency, logging, handling time, or dealing with hardware quirks? How can we write code and enable our teams to write code that really achieves zero-cost abstraction at the scale of subsystems? How do we move beyond "easy mode" code reviews recommending using algorithms over raw loops, to cultivating a sensibility for code structure that moves us closer to the above goals? What techniques are available to achieve a declarative style at scale?

These are the questions I'll address in this talk, with practical advice; case studies; and an exploration of what it means to structure code and APIs declaratively, how to do so, and what the benefits are.
---

Slides: https://github.com/boostcon/cppnow_presentations_2025/blob/main/Presentations/Declarative_Style_Evolved.pdf

think-cell develops one of the world’s leading PowerPoint applications, with C++ at the core of everything we build, from layout algorithms to deep integration with Microsoft Office. Interested in working on challenging C++ problems with real-world impact? Explore our open roles: https://www.think-cell.com/en/career/tech---

Ben Deane

Ben has been programming in C++ for this whole millennium. He spent just over 20 years in the games industry working for companies like EA and Blizzard; many of the games he worked on used to be fondly remembered but now he’s accepted that they are probably mostly forgotten. After getting more interested in modern C++, in the teens he started giving internal company talks and then talks at various conferences, spreading ideas about types, algorithms and declarative and functional techniques.

In 2018 he left the games industry and worked in finance for a short spell, writing high-frequency trading platforms using the most modern C++ that compilers could support. Now he is a Principal Engineer at Intel where he puts monads inside your CPU.


---

C++Now 2026 - 4th May - 8th May
C++Now is an annual onsite international C++ programming and coding conference held in Aspen, Colarado. For all C++ developers, C++ software engineers and those involved with the C++ language, CppNow provides an indepth and technical content provided by the best and brightest C++ experts of the C++ world.
Annual CppNow Conference - https://www.cppnow.org
https://www.linkedin.com/company/cppnow
https://twitter.com/cppnow
https://www.facebook.com/CppNow
https://www.reddit.com/r/CppNow
https://mastodon.social/@cppnow
Video Sponsors: think-cell and Bloomberg
---

Videos Filmed & Edited By Bash Films: https://bashfilms.com/
YouTube Channel Managed & Optimized By Digital Medium Ltd: https://events.digital-medium.co.uk
---

#abstraction #algorithms #boost #cpp #cplusplus #programming #coding #softwareengineering #softwaredeveloper #code #cplusplusprogramming #cplusplustutorial #cplus #softwaredevelopment

## Auto Summary

Continues a theme Ben Deane began with his 2018 talk "Easy to Use, Hard to Misuse: Declarative Style in C++," delivered at both C++Now and CppCon, which argued for writing logic as expressions that are correct by construction rather than reasoning imperatively through statements. This 2025 installment extends that idea from local code to the structure of whole subsystems and APIs, drawing on his background applying functional and monadic techniques across games, high-frequency trading, and CPU work at Intel.

