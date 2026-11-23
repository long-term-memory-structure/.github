// node --test tools/assemble.test.mjs — the assembler on planted trees: the order, a diagram, --check both ways, and
// each refusal (a missing diagram, a stray file name, an empty section, backticks in a diagram, an unknown argument).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const TOOL = join(dirname(fileURLToPath(import.meta.url)), 'assemble.mjs');
const run = (root, ...args) => spawnSync(process.execPath, [TOOL, '--root', root, ...args], { encoding: 'utf8' });

function tree(files) {
  const root = mkdtempSync(join(tmpdir(), 'assemble-'));
  mkdirSync(join(root, 'sections'));
  mkdirSync(join(root, 'diagrams'));
  mkdirSync(join(root, 'profile'));
  for (const [p, body] of Object.entries(files)) writeFileSync(join(root, p), body);
  return root;
}

const HEADER =
  '<!-- This file is assembled from sections/*.md and diagrams/*.mmd by tools/assemble.mjs. Edit those, then run: node tools/assemble.mjs -->\n\n';

test('sections join in name order, one blank line between, and a diagram line becomes its mermaid block', () => {
  const root = tree({
    'sections/20-second.md': '## Two\n\ntext two\n\n\n',
    'sections/00-first.md': '\n# One\n\ntext one\n',
    'sections/10-middle.md': '## Mid\n\n<!-- diagram: flow -->\n\nafter\n',
    'diagrams/flow.mmd': 'flowchart LR\n  a --> b\n\n',
  });
  const r = run(root);
  assert.equal(r.status, 0, r.stderr);
  const got = readFileSync(join(root, 'profile/README.md'), 'utf8');
  assert.equal(got, HEADER + '# One\n\ntext one\n\n## Mid\n\n```mermaid\nflowchart LR\n  a --> b\n```\n\nafter\n\n## Two\n\ntext two\n');
  rmSync(root, { recursive: true });
});

test('--check: 0 when the README is the assembly, 1 naming the first differing line when it is not', () => {
  const root = tree({ 'sections/00-a.md': '# A\n\nline\n' });
  assert.equal(run(root).status, 0);
  const ok = run(root, '--check');
  assert.equal(ok.status, 0, ok.stderr);
  const readme = join(root, 'profile/README.md');
  writeFileSync(readme, readFileSync(readme, 'utf8').replace('line', 'edited by hand'));
  const bad = run(root, '--check');
  assert.equal(bad.status, 1);
  assert.match(bad.stderr, /line 5 differs/);
  assert.match(bad.stderr, /"edited by hand"/);
  assert.match(bad.stderr, /move the edit into its section/);
  rmSync(root, { recursive: true });
});

test('--check with no README is 1, with the next command', () => {
  const root = tree({ 'sections/00-a.md': '# A\n' });
  const r = run(root, '--check');
  assert.equal(r.status, 1);
  assert.match(r.stderr, /does not exist\. Next: node tools\/assemble\.mjs/);
  rmSync(root, { recursive: true });
});

test('a diagram line naming a missing file is refused with its line and the diagrams that exist', () => {
  const root = tree({ 'sections/00-a.md': '# A\n\n<!-- diagram: nope -->\n', 'diagrams/real.mmd': 'flowchart LR\n' });
  const r = run(root);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /sections\/00-a\.md:3: <!-- diagram: nope --> names diagrams\/nope\.mmd, which does not exist\. Diagrams there: real\.mmd\./);
  rmSync(root, { recursive: true });
});

test('a stray file name, an empty section and backticks in a diagram are each refused, all in one run', () => {
  const root = tree({
    'sections/00-a.md': '# A\n\n<!-- diagram: tick -->\n',
    'sections/10-empty.md': '\n\n',
    'sections/notes.md': 'x\n',
    'diagrams/tick.mmd': 'flowchart LR\n```\n',
  });
  const r = run(root);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /sections\/notes\.md: not a section name/);
  assert.match(r.stderr, /sections\/10-empty\.md is empty/);
  assert.match(r.stderr, /diagrams\/tick\.mmd holds three backticks/);
  rmSync(root, { recursive: true });
});

test('an unknown argument is a usage error (2), echoed', () => {
  const root = tree({ 'sections/00-a.md': '# A\n' });
  const r = run(root, '--chek');
  assert.equal(r.status, 2);
  assert.match(r.stderr, /unknown argument "--chek"/);
  rmSync(root, { recursive: true });
});
