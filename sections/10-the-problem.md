## The Problem

### Memory is the costly part

An AI model reads and writes text in pieces called tokens; how many tokens a text makes depends on the model and the language. Its use is counted in tokens. Everything the model sees as it works is its context window: instructions, your messages, its replies, tool results. On Claude it holds up to 1 million tokens, depending on the model. Whatever the model is to remember of earlier work (the conversation so far, notes, a project's history) has to be in that window.

An agent is an AI model that works in a loop: it uses a tool, such as running a command, looks at the result, and decides the next step. Claude Code, Anthropic's coding agent, is one. It [sends "your full conversation with every request"](https://code.claude.com/docs/en/costs), so a one-line question in a conversation open all day "still draws usage for the whole conversation".

<!-- diagram: problem-every-step -->

So a fuller window costs more at every step, and works worse: as it fills, models [lose accuracy](https://www.trychroma.com/research/context-rot), which Anthropic [calls context rot](https://platform.claude.com/docs/en/build-with-claude/context-windows).

A bigger window does not end this: a lasting memory keeps growing, and outgrows any window. Even if models stopped losing track of long inputs, every step would still carry the whole window.

### Many agents at once, or one agent over time

A large project can take, by our estimate, 10 to 100 million tokens of work. It has to be split: across agents at once (horizontally), or across time (vertically), one agent going from session to session (a session is one conversation, start to end).

<!-- picture: at-once-or-over-time -->

<!-- diagram: problem-split-two-ways -->

Split across agents, the work is a swarm, of one of two kinds. Many agents can work on the same question as many tries: that is how a question is answered when no direct method is known, and a direct method, where one exists, costs far less. Or the work is divided among roles, like a team: an orchestrator agent hands parts to an architect, a coder and a tester, each a subagent.

We have done better vertically: we wrote and published a software library over a month or two of research and prototyping, with one agent carrying all the reasoning from session to session. Good results came easier and cheaper; a committee has competing aims, miscommunicates, and its talk is overhead. That is our account, not a measurement.

Others report the same. [Anthropic's article on folding subagents into one agent](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop) found, across several enterprise deployments, that one agent with skills (instructions it loads only when needed) often did better than subagents, and often cost less. Between agents, it says, you "often lose details in the back and forth"; one agent that has seen each earlier step can connect them.

<!-- picture: lost-between-agents -->

Cognition's [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) gives an example: two subagents can build a Flappy Bird game's background and bird in different styles, as neither sees the other's work.

<!-- picture: parts-that-do-not-fit -->

A 2025 study of teams of AI agents, [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) (an LLM, a large language model, is the kind of AI model this page is about), notes that such teams' gains on popular tests are "often minimal"; it gathers over 1,600 recorded runs of 7 popular multi-agent tools, and names 14 ways they fail.

Several agents do help in some cases, such as questions that branch into independent directions: [Anthropic's multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system) outperformed a single agent by 90.2% on Anthropic's internal research evaluation, for example in identifying all the board members of the companies in the S&P 500's information technology sector. By Anthropic's count, one agent uses about 4 times the tokens of a chat, and a multi-agent system about 15 times, and such systems fit poorly where every agent needs the same context. Anthropic's article on folding subagents keeps them for three cases: a window so full that the agent measurably does worse; tasks that need to run in parallel, each in a fresh window that can be thrown away afterwards; an agent unsure which tools to use, or with conflicting instructions. Our rule: start another agent when one is already fully occupied and more work comes, not by default.

That works only if one agent, over time, has a memory of its earlier sessions that it can use without filling its window.

### Every session starts from zero

A new session starts with amnesia: what it needs must be put into the window again, where it takes room from the work.

A popular memory is a wiki: linked pages that the model keeps up. Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) says reading its index first "works surprisingly well at moderate scale (~100 sources, ~hundreds of pages)". We have seen such a memory work up to some 100 to 300 linked files, depending on their size, then rot: once loaded, it leaves too little room for the work. That is the shape Thomas Jiralerspong drew for productivity with AI, a peak and then a cliff, in [Chasing the Karpathy Peak (and Falling Off Slop Cliff)](https://blog.thomas.jiralerspong.com/p/chasing-the-karpathy-peak).

When the window fills, Claude Code compacts the session, showing "Compacting conversation…": the model carries on from a summary of the older part. The summary is written before anyone knows the next question, so it guesses what will matter. A memory kept in the window must also forget to make room, yet no one knows which record a later question will need: a security audit months later, say, of a tool call that looked innocent at the time. And an old note that no longer fits the task can throw the model off.

So a long-term memory has two demands in tension: a record that keeps growing, and as little of it as possible in the window. That is the problem this project works on.
