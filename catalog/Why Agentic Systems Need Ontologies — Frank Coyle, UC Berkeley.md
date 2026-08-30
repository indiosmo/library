---
source: https://www.youtube.com/watch?v=Sir59K8ZDPU
type: video
file: "[[Why Agentic Systems Need Ontologies — Frank Coyle, UC Berkeley.webm]]"
tags: []
---

## Description

A second refund on the same order. A payout sent to the support desk instead of the buyer. An order status of "probably shipped." These are the kinds of mistakes a probabilistic agent makes and a paragraph of instructions cannot reliably stop. Frank Coyle argues that most agent failures, from brittle tools to fragile handoffs, are symptoms of one missing layer: a formal ontology sitting outside the model as logical guardrails. LLMs reason probabilistically over domains they only half understand, and no amount of prompt engineering closes that gap.

His fix is neurosymbolic: probabilistic reasoning inside, logic outside. An ontology is just typed entities, relationships, and constraints, expressed with old and boring standards like RDFS and OWL, that let you say a payment status must be one of three values, that a customer and a support rep are different things, that an order can only be refunded once. Wrap a Claude tool use loop with a validator: when the model proposes a tool call, check its types with Pydantic and its results against the ontology, and only then let it act. The catches that are painful to write in English become a few lines of logic.

Speaker info:
- https://x.com/coyle_frankp
- https://www.linkedin.com/in/frank-coyle/
- https://www.frank-coyle.ai/

Timestamps:
0:00 - Intro and an educator's philosophy
2:21 - Two lineages: agents and ontologies
4:04 - Neurosymbolic AI: guardrails around a probabilistic model
5:23 - What an ontology actually is
6:14 - Building one, and the expert systems era
7:55 - Reusing existing taxonomies
9:12 - RDFS and OWL: inference and constraints
12:12 - Agents, loops, and how they break
14:22 - A Claude tool use loop with an ontology validator
17:47 - Pydantic at the door, ontology at the ledger
18:52 - The errors an ontology catches that English cannot

