---
source: https://www.youtube.com/watch?v=P1vES9AgfC4
type: video
file: "[[Moving IO to the edges of your app- Functional Core, Imperative Shell - Scott Wlaschin.webm]]"
tags:
  - functional-programming
  - software-architecture
  - scott-wlaschin
  - f-sharp
  - hexagonal-architecture
  - domain-driven-design
  - testing
---

## Description

This talk was recorded at NDC London in London, England. #ndclondon  #ndcconferences #developer #softwaredeveloper    

Attend the next NDC conference near you: 
https://ndcconferences.com
https://ndclondon.com/

Subscribe to our YouTube channel and learn every day:   
/ @NDC 

Follow our Social Media!

https://www.facebook.com/ndcconferences
https://twitter.com/NDC_Conferences
https://www.instagram.com/ndc_conferences/

#functionalprogramming #architecture #code 

Modern architectures (such as Onion, Clean and Hexagonal) recommend that interfacing with the outside world be done at the boundaries of your app, not in the middle. Similarly, in functional programming, the core code should be deterministic, and all I/O should be at the edges.

But how can you actually do this in practice? How can you separate I/O from business logic in an elegant way?

In this talk, we'll look at some concrete examples of how to refactor code in this way. We'll also talk about how doing this improves code comprehension, testing, and refactoring.

## Auto Summary

Scott Wlaschin runs the popular fsharpforfunandprofit.com site and wrote Domain Modeling Made Functional (Pragmatic Bookshelf); he is a regular speaker at NDC, F# Exchange, and DDD Europe known for a pragmatic, non-academic take on functional programming. The "Functional Core, Imperative Shell" framing he builds on was coined by Gary Bernhardt in his 2012 SCNA talk "Boundaries" and elaborated in a Destroy All Software screencast; it is essentially Ports and Adapters / Hexagonal Architecture applied at the level of functions and values rather than services. A recurring practical theme is that pushing I/O outward lets the core be tested with fast unit tests and no mocks, and that async code, caught exceptions, or thrown exceptions inside domain logic are smells indicating I/O has leaked into the core.

