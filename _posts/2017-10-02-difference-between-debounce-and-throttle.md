---
layout: post
lang: en
title: Difference between debounce and throttle
categories: [posts]
hackernews: https://news.ycombinator.com/item?id=15382117
redirect_from:
  - /blog/difference-between-debounce-and-throttle
  - /essays/difference-between-debounce-and-throttle
---

[Debounce](https://lodash.com/docs/4.17.11#debounce) is like hitting the snooze button on your alarm clock. You are trying to wake up,
but you’re just not there yet. Debounce is you saying not yet, not yet,
not yet&mdash;and this could go on forever. Theoretically you might never wake up.
A real world example might be preventing a chart from being redrawn while the window
is resized by some maniac who has nothing better to do than expand and shrink his
browser incessantly for five minutes.
Only when the activity stops for, say, two seconds will the chart be redrawn.

With [throttling](https://lodash.com/docs/4.17.11#throttle), on the other hand,
something _will_ happen every so often.
Let’s say the maniac above decides to click a button that reloads the chart
over and over again putting a strain on your backend.
With throttle, the data would be fetched from the backend, but only every ten seconds.
