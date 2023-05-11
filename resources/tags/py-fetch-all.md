---
title: "Python fetch all items"
---

> The following code can fetch all items inside of a base in python

```py
    res = db.fetch()
    items = res.items
    while res.last:
        res = db.fetch(last=res.last)
        items += res.items
```
