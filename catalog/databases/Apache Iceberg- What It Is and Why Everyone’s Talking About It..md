---
source: https://www.youtube.com/watch?v=TsmhRZElPvM
type: video
file: "[[Apache Iceberg- What It Is and Why Everyone’s Talking About It..webm]]"
tags:
  - data-engineering
  - data-lake
  - apache-kafka
  - stream-processing
  - tim-berglund
  - lightboard
---

## Description

More Info: https://cnfl.io/4i2M17x | You’ve probably heard about Apache Iceberg™—after all, it’s been getting a lot of buzz. But what actually is it? And why are so many people excited about using it with streaming data?

In this lightboard, Tim Berglund breaks it all down in a way that makes sense, even if you’re new to Iceberg. He walks through the history that led to Iceberg’s emergence, explains how it works under the hood, and shares how it fits into the bigger picture of modern data systems and streaming data.

He also reveals something we’ve been working on at Confluent called TableFlow—a way to make your Apache Kafka® topic data accessible as an Iceberg table in your data lake, without needing to bolt together a bunch of different tools. If you're the kind of person who likes querying data lakes and streaming systems, you’ll probably want to check this out.

Whether you're deep into data infrastructure or just curious about what's next, this is a super approachable intro to a technology that’s becoming a big deal.

RELATED RESOURCES
► TableFlow Announcement Blog: https://cnfl.io/4j26B9y
► Try Confluent Cloud for Free: https://cnfl.io/4ibAYcl Discount code: CONFLUENTDEV1

CHAPTERS
00:00 - The Emergence of Iceberg: A Brief History
01:00 - The Rise of the Data Lake 
02:48 - Why Iceberg needed to exist
03:48 - Iceberg’s Architecture: How It Works in the Modern Streaming World
10:27 - Iceberg’s Infrastructure: What is It Made Of?
11:59 - Tableflow: Kafka Topics as Iceberg Tables

–

CONNECT
Subscribe, if you dare: https://www.youtube.com/@ConfluentDeveloper?sub_confirmation=1
Community Slack: https://confluentcommunity.slack.com
X: https://x.com/confluentinc
Linkedin: https://www.linkedin.com/company/confluent
GitHub: https://github.com/confluentinc
Site: https://developer.confluent.io

ABOUT CONFLUENT DEVELOPER
Confluent Developer provides comprehensive resources for developers looking to learn about Apache Kafka®, Apache Flink®, Confluent Cloud, Confluent Platform, and any other technology related to the broader Data Streaming Platform. Content on Confluent Developer includes courses, getting started guides, topical deep-dives, patterns, tutorials, and listings of community events. Learn more at https://developer.confluent.io. 

#apacheiceberg #tableflow #apachekafka #kafka #confluent

## Auto Summary

Tim Berglund is Confluent's VP of Developer Relations, known for his whiteboard-style explainer videos on the Confluent Developer channel. Apache Iceberg itself originated at Netflix around 2017, created by Ryan Blue and Dan Weeks to fix correctness and performance problems with Hive tables on object storage, and was donated to the Apache Software Foundation in 2018. The lightboard covers Iceberg's three-layer design of catalog, metadata (manifest lists and manifest files), and Parquet data files, which enables ACID transactions, schema evolution, and time travel on a data lake; TableFlow, announced by Confluent in 2024, materializes Kafka topics directly as Iceberg tables to bridge streaming and analytical systems.

