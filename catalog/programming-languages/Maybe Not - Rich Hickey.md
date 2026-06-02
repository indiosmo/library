---
source: https://www.youtube.com/watch?v=YR5WdGrpoug
type: video
file: "[[Maybe Not - Rich Hickey.webm]]"
tags:
  - clojure
  - rich-hickey
  - type-systems
  - functional-programming
  - clojure-spec
  - null-references
  - conference-talk
---


## Auto Summary

Rich Hickey, creator of Clojure, delivered this talk at Clojure/conj 2018 as conceptual groundwork for clojure.spec's handling of optional information. He opens from Tony Hoare's "billion-dollar mistake" (the 1965 null reference) and argues that wrapping values in Maybe/Option/Either is itself a mistake: it conflates the orthogonal concerns of a value's type and its presence, breaks API compatibility when you make an argument or return optional, and substitutes for genuine first-class union types (as found in Kotlin's nullable types or Dotty's union types). He contrasts this with Clojure's preference for maps over records, where an absent key simply has no entry rather than a nil placeholder, and previews spec's nilable and or constructs.

