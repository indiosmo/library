---
source: https://www.youtube.com/watch?v=zULU6Hhp42w
type: video
file: "[[Better Code- Concurrency - Sean Parent.webm]]"
series: "[[Better Code]]"
tags:
  - c-plus-plus
  - concurrency
  - parallelism
  - sean-parent
  - amdahls-law
  - futures
  - lecture
---

## Description

Despite all of the recent interest, concurrency in standard C++ is still barely in its infancy.
This talk uses the primitives supplied by C++14 to build a simple, reference, implementation of a task system. The goal is to learn to write software that doesn’t wait.



NDC Conferences
https://ndc-london.com
https://ndcconferences.com

## Auto Summary

Sean Parent, then a principal scientist on Adobe's digital imaging group (a Photoshop and Lightroom veteran who also worked on Apple's PowerPC transition and a year on Google's Chrome OS), gives this NDC London edition of a talk he repeated at CppCon 2015 and C++Now. Beyond building the C++14 task system, he develops a conceptual model for futures and continuations and points toward communicating sequential processes and higher-level concurrent constructs; a reference implementation of the task system has since been published on GitHub. Parent later flagged an erratum, noting he misstated that std::async changed with C++14.

