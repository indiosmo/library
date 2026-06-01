---
source: https://www.youtube.com/watch?v=iDWwoz9ZUzw
type: video
file: "[[Design Good Schemas - Get a Better Database - Nuri Halperin - NDC Oslo 2023.mkv]]"
tags:
  - databases
  - data-modeling
  - normalization
  - relational-databases
  - ndc-oslo
  - lecture
  - software-architecture
---

## Description

Table schemas in relational databases have a huge impact on your future performance and ability to maintain your application. In a world of CI/CD this is amplified since it can hold back your deployments and flexibility.

So how do you design tables that serve your applications well? Is normalization to the Nth degree sufficient? Can't I just throw an index on a table and get good performance? Just develop a POCO/POJO and let your ORM take care of it? (No, no, and no!)

In this session, you'll find out how to step up your schema-design game by adopting a relational mentality. The session will cover aspects of modeling, mapping models to tables, and all the way down to data types and fields.


Check out our new channel: 
NDC Clips:
@ndcclips

Check out more of our featured speakers and talks at
https://ndcconferences.com/
https://ndcoslo.com/

## Auto Summary

Nuri Halperin is a software architect, Pluralsight author, Microsoft MVP alum, and MongoDB Champion who has consulted on scalable data systems for over two decades. This NDC Oslo 2023 talk argues against treating schema as an afterthought of ORM-generated POCO/POJO classes, drawing a sharp distinction between a domain model and a relational schema and warning that poor early choices compound under CI/CD. The chapters work through concrete antipatterns the description leaves unnamed: multi-entity tables, an 'Abnormal Form' of over-denormalization, sequential versus natural primary keys, and the friction between ad-hoc DDL and disciplined migration scripts.

