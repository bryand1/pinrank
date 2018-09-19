# Pinrank


Find the most saved pins on Pinterest for a given search term.


## Usage

```python
from pinrank import Pinrank

pr = Pinrank.login("user@example.com", "p@ssw0rd")
pins = pr.search("halloween costumes")
saves = pr.saves(pins)
```
