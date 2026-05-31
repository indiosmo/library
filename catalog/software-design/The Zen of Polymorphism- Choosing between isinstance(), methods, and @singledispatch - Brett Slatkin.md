---
source: https://www.youtube.com/watch?v=hidy15rK2a4
type: video
file: "[[The Zen of Polymorphism- Choosing between isinstance(), methods, and @singledispatch - Brett Slatkin.webm]]"
tags:
  - python
  - polymorphism
  - object-oriented-programming
  - functional-programming
  - singledispatch
  - brett-slatkin
  - conference-talk
---

## Description

Python is a multi-paradigm language that embraces both functional programming and object-oriented programming (OOP) approaches to writing code. OOP is especially popular, in large part due to how it enables polymorphism (for example, calling speak() on a Dog object returns "woof", while a Cat object's method returns "meow".) However, OOP has many downsides that are often not understood until it's too late in the lifecycle of building a program. Fortunately, Python also enables developers to achieve similar behavior to polymorphism while using simple functions and plain data objects instead of classes.

This talk will detail three different approaches provided by Python to achieve polymorphism behavior in a realistic program. It will compare and contrast their relative strengths and weaknesses. It will show how the most naive approach, which relies on isinstance() checks, leads to severe code duplication. It will show how OOP method polymorphism leads to code being organized along the wrong axis, which hurts understandability, debugging, and maintainability in practice. It will also demonstrate a less commonly known part of the built-in functools library called @singledispatch that strikes a perfect balance between functional and OOP programming styles.

Finally, you'll learn how @singledispatch works under the covers, and how to build or integrate similar functionality into your own programs so you can realize the benefits of polymorphism while avoiding the pitfalls.

## Auto Summary

Brett Slatkin is a principal software engineer at Google and the author of "Effective Python: 90 Specific Ways to Write Better Python." The title riffs on Tim Peters' "Zen of Python," and the @singledispatch tool it champions comes from PEP 443, which added single-dispatch generic functions to functools in Python 3.4. The talk reflects a recurring theme in Slatkin's writing: favoring plain functions and data over deep class hierarchies, here arguing that singledispatch organizes code along the data-type axis without the maintainability costs of method-based polymorphism.

