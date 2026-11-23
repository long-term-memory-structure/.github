### The other two packages

#### [ltms-reader](https://github.com/long-term-memory-structure/ltms-reader): read your sessions yourself

```sh
npx ltms-reader
```

A full-screen terminal view of your sessions, down to the text behind every address ltms prints.

#### [ltms-semantic](https://github.com/long-term-memory-structure/ltms-semantic): search by meaning

`ltms search` needs your words to be in the turn. `ltms-semantic search` ranks the turns by how near they are in meaning to your question, even in other words or another language. It needs Node.js 22.13.0 or newer and downloads its 2.28 GB model once; [its README](https://github.com/long-term-memory-structure/ltms-semantic) has the install steps.
