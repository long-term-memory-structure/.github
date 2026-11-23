### Try it

You need Node.js 20 or newer, and a project you have worked on with Claude Code.

#### 1. Install ltms

```sh
npm install -g long-term-memory-structure
```

Without installing, `npx long-term-memory-structure` works wherever this page says `ltms`. Do not run `npx ltms`: this package does not hold that name on npm.

#### 2. List a project's sessions

Claude Code keeps each project's transcripts in a folder under `~/.claude/projects/` (or `$CLAUDE_CONFIG_DIR/projects/`, if you set that), named after the project's path: every character other than a–z, A–Z or 0–9 becomes `-`, so `/home/me/my.app` becomes `-home-me-my-app`. Find yours with `ls ~/.claude/projects/`, then:

```sh
ltms index ~/.claude/projects/-home-me-my-app
```

The folder holds one transcript per session: the session's prompts, replies, tool calls (a command run, a file read or changed) and results, one record per line.

`ltms index` answers in JSON lines: first a line that says what it read, then one line per session, newest first, 20 at a time (the first line gives the command for the next 20): when it ran, its turns, tool calls, failed calls and compactions, and addresses. A turn is a prompt and the work after it. An address names a transcript by the first 8 characters of its name, the session's id, and a place in it: `1a2b3c4d:L120` is line 120, and `1a2b3c4d:T003` is the third turn.

ltms prints where things are, not your prompts or the agent's replies. To read those, run `npx ltms-reader`, then type `:`, the address, and Enter.

`ltms search 'migration rollback' ~/.claude/projects/-home-me-my-app` finds the turns that hold every word, and answers with addresses too.

#### 3. Give your agent the skill

A skill is a short instruction file that Claude Code reads from `~/.claude/skills/`. This one teaches your agent these commands, and tells it to use them before asking you to repeat something. The line uses `npx`, so it works with or without step 1:

```sh
mkdir -p ~/.claude/skills/ltms && npx -y long-term-memory-structure@0.3 skill > ~/.claude/skills/ltms/SKILL.md.tmp && mv ~/.claude/skills/ltms/SKILL.md.tmp ~/.claude/skills/ltms/SKILL.md
```

While it uses the skill, your agent may run, without asking you, four commands that only read: `index`, `skeleton`, `search` and `stats` (which counts a transcript's turns, calls and failures). `pin` is not one of them. In a new session, you can ask it, for example: "Use ltms to find where we decided to drop the old login page."

#### 4. Pin your transcripts

Claude Code deletes transcripts older than 30 days by default (its `cleanupPeriodDays` setting). `ltms pin` copies them where that cleanup does not reach; `--check` reads the copies back and counts what is missing:

```sh
ltms pin ~/.claude/projects --to ~/claude-pins
ltms pin --check ~/claude-pins
```

A pin copies only what exists when it runs; [the ltms README](https://github.com/long-term-memory-structure/long-term-memory-structure/blob/v0.3.1/README.md#ltms-pin-path---to-dir) shows how to pin after every session and on a schedule. The copies hold everything, secrets included: keep them private.
