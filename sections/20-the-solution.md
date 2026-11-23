## The Solution

We take the memory out of the window. With our open-source tools (ltms and two companions, below), your agent, and you, can still find and reread what was said or done in earlier sessions, or, as far as we measured (Claude Code's `/compact` command), before a compaction. This already works with Claude Code, on your own computer.

### Outside the window, read by address

The design, in four rules:

1. **Keep everything.** Delete nothing to make room; let no summary replace the record. Correct a mistake with a new record, and keep both: this is what "append-only ledgers" and "heal by addition" mean above.
2. **Keep it outside the window.** Claude Code already writes each session to a file on your computer, its transcript, one record per line: prompts, replies, tool calls, their results, and more. A compaction, as far as we measured, only adds to that file: the details leave the model's view, not the disk. (Claude Code deletes these files after 30 days by default; `ltms pin`, below, keeps copies.)
3. **Reach it by address.** Every line has an address, such as `1a2b3c4d:L120`: line 120 of the session whose file name begins `1a2b3c4d`.
4. **Read only the line needed.** The agent reads a small outline of a session (a line per turn and per tool call, each with its address; a turn is a prompt and the work after it), then, from the outline or a search, the one line it needs, not the whole session. The aim: a small fixed cost in every session (the skill's short description; the skill itself, a short instruction file that teaches your agent the commands, loads when it is used), and a small cost per search.

Below, the same context window, with a memory kept in it and with ltms.

<!-- diagram: solution-memory-in-window-or-on-disk -->

### Search by meaning, answered with addresses

A search by meaning finds what was said even in other words. It turns each passage into an embedding (or vector): a list of numbers, close for passages close in meaning. The usual way, called RAG (retrieval-augmented generation), puts the nearest passages' text into the window. Ours, `ltms-semantic`, answers with addresses instead, not with the passages' text or their vectors; then you read only the line you need, word for word, at its address. We call this RAGDAG. `ltms-semantic` does it today, with ltms's addresses (a session and a turn or a line in it); in the larger design below, the addresses would be hashes in a DAG (a directed acyclic graph).

<!-- diagram: solution-ragdag -->

### What exists now, and the larger design

Three open-source packages do rules 3 and 4, and part of rule 1, on your own machine:

- [`long-term-memory-structure`](https://github.com/long-term-memory-structure/long-term-memory-structure) (the command `ltms`) gives your agent the outline and the addresses, and finds the turns that hold given words. `ltms pin` keeps copies of the session files past Claude Code's cleanup; once it has copied a version of a file, ltms keeps that version, also when the file is later rewritten, and its README lists the cases in which ltms can still write over one.
- [`ltms-reader`](https://github.com/long-term-memory-structure/ltms-reader) shows you the text at an address.
- [`ltms-semantic`](https://github.com/long-term-memory-structure/ltms-semantic) searches by meaning, and answers with the same addresses.

A map, a separate program, shows people the same history, by the same addresses. It is not open source or published yet; a picture is in the technicals below.

The larger design goes further; these are its ideas, not the packages' features. In the packages, an address is the start of a session file's name and a line or a turn in it. In the design, each record is filed under its hash, a short code computed from its contents, so a changed record no longer matches its code. Records point back to earlier ones by hash, a shape called a [DAG](https://docs.ipfs.tech/concepts/merkle-dag/) (the DAG in RAGDAG); a search by meaning answers with those hashes.

The technicals below show how to install and use ltms, how to open ltms-reader, and what ltms-semantic needs.
