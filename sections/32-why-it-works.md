### Why it works

Measured with `/compact` on Claude Code 2.1.270 and 2.1.300, compaction only adds to the transcript; on 2.1.300 the summary also names the transcript's file. Automatic compaction, and compaction after tool calls, were not tested. What each model's summary kept, measured: [the compaction page](https://long-term-memory-structure.github.io/long-term-memory-structure/compaction.html).

But the file is hard to read back: one line can be hundreds of kilobytes.

So ltms gives the agent a small outline of each transcript. `ltms skeleton` prints a line per turn and per tool call, like this one from ltms's test transcript `demo.jsonl`, whose addresses start with `demo.jso`:

```
{"k":"call","a":"demo.jso:L24","ta":"demo.jso:T003","tool":"Bash","verb":"npm","in":"84c7c646123a","ok":false,"ek":"exit-1","r":"demo.jso:L25","out":"429ad9a9f725","n":58}
```

<!-- diagram: technicals-address-to-line -->

In turn 3, the agent ran `npm` and it failed with exit code 1; the call is on line 24, its result on line 25. Line 25 holds what the outline leaves out: `FAIL test/add.test.js`, `expected 4, received 5`. The agent reads that one line, as the skill shows it, not the whole session. [The ltms README](https://github.com/long-term-memory-structure/long-term-memory-structure/blob/v0.3.1/README.md#ltms-skeleton-filejsonl) explains every field.

On 2,539 transcripts, that outline came to 0.7 % of their size, so it fits in a context window where the transcript does not.

ltms is the first piece of a larger design. The main README's [Intent and tradeoffs](https://github.com/long-term-memory-structure/long-term-memory-structure/blob/v0.3.1/README.md#intent-and-tradeoffs) lists its aims and what each costs.
