---
source: https://www.youtube.com/watch?v=2JB1_e5wZmU
type: video
file: "[[Domain Modeling Made Functional - Scott Wlaschin - KanDDDinsky 2019.mkv]]"
tags:
  - functional-programming
  - domain-driven-design
  - f-sharp
  - type-systems
  - scott-wlaschin
  - conference-talk
---

## Description

Statically typed functional programming languages encourage a very different way of thinking about types. The type system is your friend, not an annoyance, and can be used in many ways that might not be familiar to OO programmers. Types can be used to represent the domain in a fine-grained, self documenting way. And in many cases, types can even be used to encode business rules so that you literally cannot create incorrect code. You can then use the static type checking almost as an instant unit test — making sure that your code is correct at compile time. In this talk, we'll look at some of the ways you can use types as part of a domain driven design process, with some simple real world examples in F#. No jargon, no maths, and no prior F# experience necessary.

## Auto Summary

Scott Wlaschin is the creator of the F# for Fun and Profit site (fsharpforfunandprofit.com) and the talk distills his 2018 Pragmatic Bookshelf book of the same name, which marries Eric Evans-style domain-driven design with statically typed functional programming. KanDDDinsky is a Berlin domain-driven design conference; the talk's running thread is using an algebraic type system (composing types with AND for records and OR for choice/sum types) to make illegal states unrepresentable, so the compiler enforces business rules as a near-instant unit test. The chapter list maps onto the book's progression from a shared mental model captured in code, through choice types and optional values, to constrained 'wrapper' types for domain primitives.

