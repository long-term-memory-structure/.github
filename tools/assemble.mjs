#!/usr/bin/env node
// tools/assemble.mjs: profile/README.md is assembled from sections/*.md, in file-name order (00-…, 10-…, 20-…). A line
// that is exactly `<!-- diagram: NAME -->` becomes a ```mermaid block holding diagrams/NAME.mmd. The sections and the
// diagrams are the sources; the README is never edited by hand. The website reads the same sources.
//
//   node tools/assemble.mjs                 write profile/README.md
//   node tools/assemble.mjs --check         exit 0 if profile/README.md is the assembly, else 1 (the first line that differs)
//   node tools/assemble.mjs --root DIR ...  assemble DIR instead of this repository (the tests use it)
//
// Exit: 0 written or equal · 1 the README differs, or a section or a diagram is wrong (each named, with its fix) · 2 usage.
import { readFileSync, writeFileSync, readdirSync, renameSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const USAGE = 'usage: node tools/assemble.mjs [--check] [--root DIR]';
const HEADER =
  '<!-- This file is assembled from sections/*.md and diagrams/*.mmd by tools/assemble.mjs. Edit those, then run: node tools/assemble.mjs -->\n\n';
const SECTION_NAME = /^\d\d-[a-z0-9-]+\.md$/;
const DIRECTIVE = /^<!-- diagram: ([a-z0-9-]+) -->$/;

function fail(code, message) {
  process.stderr.write(message.endsWith('\n') ? message : message + '\n');
  process.exit(code);
}

function parseArgs(argv) {
  const opts = { check: false, root: resolve(dirname(fileURLToPath(import.meta.url)), '..') };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--check') opts.check = true;
    else if (a === '--root') {
      if (i + 1 >= argv.length) fail(2, `assemble: --root needs a directory.\n${USAGE}`);
      opts.root = resolve(argv[++i]);
    } else fail(2, `assemble: unknown argument ${JSON.stringify(a)}.\n${USAGE}`);
  }
  return opts;
}

// The assembly of root's sections, as one string; every problem found is thrown together, each with its fix.
export function assemble(root) {
  const sectionsDir = join(root, 'sections');
  const diagramsDir = join(root, 'diagrams');
  if (!existsSync(sectionsDir)) throw new Error(`${sectionsDir} does not exist: the README is assembled from it.`);
  const all = readdirSync(sectionsDir).sort();
  const problems = [];
  const stray = all.filter((f) => !SECTION_NAME.test(f));
  for (const f of stray)
    problems.push(`sections/${f}: not a section name (two digits, a dash, lower-case words, .md, such as 10-the-problem.md): rename or remove it.`);
  const files = all.filter((f) => SECTION_NAME.test(f));
  if (!files.length && !stray.length) problems.push(`sections/ holds no section (NN-name.md).`);
  const diagrams = existsSync(diagramsDir) ? readdirSync(diagramsDir).filter((f) => f.endsWith('.mmd')).sort() : [];
  const parts = [];
  for (const f of files) {
    const lines = readFileSync(join(sectionsDir, f), 'utf8').replace(/\r\n/g, '\n').split('\n');
    const out = [];
    lines.forEach((line, i) => {
      const m = DIRECTIVE.exec(line);
      if (!m) return out.push(line);
      const name = m[1];
      const path = join(diagramsDir, name + '.mmd');
      if (!existsSync(path)) {
        problems.push(`sections/${f}:${i + 1}: ${line} names diagrams/${name}.mmd, which does not exist. Diagrams there: ${diagrams.join(', ') || 'none'}.`);
        return out.push(line);
      }
      const body = readFileSync(path, 'utf8').replace(/\r\n/g, '\n').replace(/\n+$/, '');
      if (body.includes('```')) problems.push(`diagrams/${name}.mmd holds three backticks, which would end the README's code block: remove them.`);
      out.push('```mermaid', body, '```');
    });
    const text = out.join('\n').replace(/^\n+/, '').replace(/\s+$/, '');
    if (!text) problems.push(`sections/${f} is empty: write the section or remove the file.`);
    parts.push(text);
  }
  if (problems.length) throw new Error(problems.join('\n'));
  return HEADER + parts.join('\n\n') + '\n';
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  let text;
  try {
    text = assemble(opts.root);
  } catch (e) {
    fail(1, `assemble: ${opts.root}:\n${e.message}`);
  }
  const readme = join(opts.root, 'profile', 'README.md');
  if (opts.check) {
    const have = existsSync(readme) ? readFileSync(readme, 'utf8') : null;
    if (have === text) {
      process.stdout.write(`assemble --check: ${readme} is the assembly of sections/ (${text.split('\n').length - 1} lines).\n`);
      return;
    }
    if (have === null) fail(1, `assemble --check: ${readme} does not exist. Next: node tools/assemble.mjs`);
    const a = have.split('\n');
    const b = text.split('\n');
    let n = 0;
    while (n < a.length && n < b.length && a[n] === b[n]) n++;
    const clip = (s) => (s === undefined ? '(no line)' : JSON.stringify(s.length > 160 ? s.slice(0, 160) + '…' : s));
    fail(
      1,
      `assemble --check: ${readme} is not the assembly of sections/: line ${n + 1} differs.\n` +
        `  README:   ${clip(a[n])}\n  assembly: ${clip(b[n])}\n` +
        `Next: if the README was edited by hand, move the edit into its section; then run node tools/assemble.mjs`,
    );
  }
  const tmp = readme + '.tmp';
  writeFileSync(tmp, text);
  renameSync(tmp, readme);
  process.stdout.write(`assemble: wrote ${readme} (${text.split('\n').length - 1} lines) from ${readdirSync(join(opts.root, 'sections')).filter((f) => SECTION_NAME.test(f)).length} sections.\n`);
}

if (import.meta.url === `file://${process.argv[1]}`) main();
