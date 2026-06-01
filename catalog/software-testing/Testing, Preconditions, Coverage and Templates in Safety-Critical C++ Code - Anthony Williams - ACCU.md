---
source: https://www.youtube.com/watch?v=L9jiRanMPnQ
type: video
file: "[[Testing, Preconditions, Coverage and Templates in Safety-Critical C++ Code - Anthony Williams - ACCU.webm]]"
tags:
  - cpp
  - software-testing
  - code-coverage
  - templates
  - functional-safety
  - automotive-software
  - anthony-williams
---

## Description

ACCU Membership: https://tinyurl.com/ydnfkcyn
---

Testing, Preconditions, Coverage and Templates in Safety-Critical C++ Code - Anthony Williams - ACCU 2025
---

Safety Critical code requires extensive testing to verify that the code does what it is supposed to do. This often maps to "code coverage" requirements.

For code that has preconditions, we may want to test that the precondition is checked, and results in the precondition violation handler being called.

For template code, every instantiation of a template is distinct. If your tests exercise a specific instantiation, that doesn't mean that other instantiations have the same behaviour: there might be template specializations with different behaviour, or the functions found during overload resolution with a different set of template parameters might have different behaviour.

This talk will go into more specifics about these areas, and ways that my team has found to address them.

Slides: https://accu.org/conf-previous/accu2025/

Join think-cell as a C++ Developer and work on cutting-edge challenges with a focus on code excellence, innovation, and working alongside an international team of experts — apply now to be part of a team shaping the future of business presentations. https://www.think-cell.com/en/career
---

Anthony Williams

Anthony Williams is the author of C++ Concurrency In Action, and a developer with over 20 years of experience, mostly using C++. He has been involved in the C++ standardization process since 2001, and spent many years as a consultant and trainer.

He currently works for Woven by Toyota, writing in-vehicle software for the next generation of Toyota cars.

Video Sponsored By JetBrains
---

The ACCU Conference is the annual conference of the ACCU membership, but is open to any and all who wish to attend. The tagline for the ACCU is 'Professionalism in Programming', which captures the whole spectrum of programming languages, tools, techniques and processes involved in advancing our craft. While there remains a core of C and C++ - with many members participating in respective ISO standards bodies - the conference, like the organisation, embraces other language ecosystems and you should expect to see sessions on C#, D, F#, Go, Javascript, Haskell, Java, Kotlin, Lisp, Python, Ruby, Rust, Swift and more.The ACCU Conference is a conference by programmers for programmers about programming.
Discounted rates for members.
ACCU Membership: https://tinyurl.com/ydnfkcyn
2025 Program: https://accu.org/conf-previous/accu2025/
https://accu.org
https://www.accuconference.org/
https://mastodon.social/@ACCUConf
https://www.linkedin.com/showcase/accu-conference/
https://bsky.app/profile/accuconf.bsky.social
https://www.facebook.com/accuorg
https://www.reddit.com/r/ACCUConf/
---

YouTube Videos Filmed, Edited & Optimised by Digital Medium: https://events.digital-medium.co.uk

#accuconf #cppprogramming #cpp #cplusplus #cplusplusprogramming #programming #softwaredevelopment #softwareengineer #programmingconcepts #coding #programmingtutorial #code #software #softwareengineeringlectures

## Auto Summary

Anthony Williams is best known as the maintainer of the Boost Thread library and the author of the just::thread and just::thread Pro implementations of the C++11 thread library through his firm Just Software Solutions; he has sat on the BSI C++ Standards Panel since 2001 and authored many of the committee papers behind C++11's threading support. The safety-critical practices he describes are shaped by automotive functional-safety standards such as ISO 26262, where coverage criteria like MC/DC (modified condition/decision coverage) and verifiable precondition checking are mandated rather than optional. ACCU 2025 was the Bristol, UK conference of the ACCU ('Professionalism in Programming'), the same community whose Standards-panel roots first drew Williams into C++ standardization.

