### What stays on your machine

Installing downloads each package and its dependencies from the npm registry (on Linux x64, ltms-semantic's install can also download GPU libraries it does not use, from NuGet rather than npm; its README shows how to skip them), and `npx` asks the registry on every run. When they run:

| Package | Needs | Network |
|---|---|---|
| `long-term-memory-structure` (`ltms`) | Node.js 20 or newer; no dependencies | None, and it collects no usage data |
| `ltms-reader` | Node.js 20 or newer | None, and it writes no file |
| `ltms-semantic` | Node.js 22.13.0 or newer; at least 4 GiB of memory to index; tested on Linux x64 only | Only `model fetch`, which downloads the model from Hugging Face |

ltms-semantic's store, on your disk, holds none of your transcripts' text (it keeps their paths), but text can be partly recovered from its vectors: keep it as private as `~/.claude`.

A line your agent reads back from a transcript enters its context, which Claude Code sends to the model with every request: a transcript holds everything that was said and run, secrets included, and an old tool result can hold instructions planted by whoever wrote the page or file it came from. The skill tells your agent to read only the parts the task needs, which limits how much of that text enters, not what it says; nothing in ltms or the skill marks it as untrusted. Like a web page your agent opens, it is data that can still mislead your agent, not instructions to follow.
