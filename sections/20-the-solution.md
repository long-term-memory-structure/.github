## The Solution

We take the memory out of the window. Your agent, and you, can still find and reread what was said or done in earlier sessions, or before a compaction. Today this works with Claude Code on your own computer.

### Outside the window, read by address

The design, in four rules:

1. **Keep everything.** Delete nothing to make room; let no summary replace the record. Correct a mistake with a new record, and keep both: this is what "append only ledgers" and "heal by addition" mean above.
2. **Keep it outside the window.** Claude Code already writes each session to a file on your computer, its transcript: one line per prompt, reply, tool call or result. A compaction, as far as we measured, only adds to that file: the details leave the model's view, not the disk. (Claude Code deletes these files after 30 days by default; `ltms pin`, below, keeps copies.)
3. **Reach it by address.** Every line has an address, such as `1a2b3c4d:L120`: line 120 of the session whose file name begins `1a2b3c4d`.
4. **Read only the line needed.** The agent reads a small outline of a session (a line per turn and per tool call, each with its address), then the one line it needs, not the whole session. The aim: a small fixed cost in every session (the skill), and a small cost per search.

Below, the same context window, today and with ltms, our open-source tool.

<!-- diagram: solution-today-with-ltms -->

### Search by meaning, answered with addresses

A search by meaning finds what was said even in other words. It turns each passage into an embedding (or vector): a list of numbers, close for passages close in meaning. The usual way, called RAG, puts the nearest passages' text into the window. Ours, `ltms-semantic`, answers with addresses instead, not with the passages' text or their vectors; then only the line needed is read, word for word, at its address. We call this RAGDAG: `ltms-semantic` does it today, with line addresses; in the larger design below, the addresses are hashes in a DAG.

<!-- diagram: solution-ragdag -->

### What exists today, and the larger design

Today, three open-source packages do rules 3 and 4, on your own machine:

- [`long-term-memory-structure`](https://github.com/long-term-memory-structure/long-term-memory-structure) (the command `ltms`) gives your agent the outline and the addresses, and finds the turns that hold given words. `ltms pin` does part of rule 1: it keeps copies of the session files past Claude Code's 30-day cleanup; once it has copied a version of a file, ltms never deletes it or writes over it (its README lists the limits).
- [`ltms-reader`](https://github.com/long-term-memory-structure/ltms-reader) shows you the text at an address.
- [`ltms-semantic`](https://github.com/long-term-memory-structure/ltms-semantic) searches by meaning, and answers with the same addresses.

A map shows people the same history, by the same addresses. It is not open source or published yet; a picture is in the technicals below.

The larger design goes further; these are its ideas, not the packages' features. In the packages, an address is the start of a session file's name and a line or a turn in it. In the design, each record is filed under its hash, a short code computed from its contents, so any change shows. Records point back to earlier ones by hash, a shape called a [DAG](https://docs.ipfs.tech/concepts/merkle-dag/) (the DAG in RAGDAG); a search by meaning answers with those hashes.

The technicals below show how to install and use the three packages.
