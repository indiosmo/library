---
source: https://www.youtube.com/watch?v=24q8WNgYrJE
type: video
file: "[[More Testing, Fewer Tests.webm]]"
tags:
  - elixir
  - property-based-testing
  - test-coverage
  - software-engineering
  - lecture
  - 2020s
---

## Description

ElixirConf US 2024 - Tyler Young

https://2024.elixirconf.com/#speakers-presenter-tyler-young


Tests are the best way to gain confidence your system is working as designed, but tests aren’t free. They take time to create in the first place, and they represent a maintenance burden for your organization just like production code—in some cases worse, because having many tests can ossify the current functionality and make it more work to change in the future.

Reading tests can also be a way to communicate the business domain the system is designed to handle. This is particularly useful in debugging; if there’s an existing test case that should cover this behavior, you can make it fail before fixing the bug.

For each of these use cases, having more tests is actually a negative, all else being equal. If you could gain the same level of coverage while writing fewer tests and taking less time to create them initially, you accelerate development, reduce the maintenance burden, and improve the clarity of the tests as a communication tool.

In this talk, we’ll examine two ways of maintaining or increasing test coverage and confidence with fewer tests: using table-based examples in tests, and using property-based testing. We’ll discuss when to choose one over the other, what the tradeoffs are compared to the naive approach of many tests, and how to get your team on board with a philosophy around these types of tests.

## Auto Summary

Tyler A. Young is a product-focused Elixir developer and frequent ElixirConf presenter (he also spoke in 2023 and gave 2025's "Cat and Mouse: Challenges in Adversarial Web Scraping"). The talk's two techniques map to established Elixir tooling: table-based examples are typically driven by ExUnit's `for`-comprehension or parameterized cases, while property-based testing in Elixir is conventionally done with StreamData (the library behind ExUnitProperties). Young notes his slides depend heavily on the accompanying code samples, especially the test directory.

