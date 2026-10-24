import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm, readFile, writeFile, readdir, lstat, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const installer = fileURLToPath(new URL('../scripts/install-skill.mjs', import.meta.url));
const source = fileURLToPath(new URL('../skills/groovectl', import.meta.url));
const run = (...args) => spawnSync(process.execPath, [installer, ...args], { encoding: 'utf8', timeout: 10_000 });

async function compareTrees(left, right) {
  const names = (await readdir(left)).sort();
  assert.deepEqual((await readdir(right)).sort(), names);
  for (const name of names) {
    const a = join(left, name);
    const b = join(right, name);
    if ((await lstat(a)).isDirectory()) await compareTrees(a, b);
    else assert.deepEqual(await readFile(b), await readFile(a));
  }
}

test('installs the complete portable skill into a directory with spaces', async () => {
  const root = await mkdtemp(join(tmpdir(), 'groovectl skill test '));
  try {
    const result = run('--skills-dir', join(root, 'agent skills'));
    assert.equal(result.status, 0, result.stderr);
    await compareTrees(source, join(root, 'agent skills', 'groovectl'));
  } finally { await rm(root, { recursive: true, force: true }); }
});

test('refuses to overwrite existing content', async () => {
  const root = await mkdtemp(join(tmpdir(), 'groovectl-skill-test-'));
  try {
    assert.equal(run('--skills-dir', root).status, 0);
    const file = join(root, 'groovectl', 'SKILL.md');
    await writeFile(file, 'user customization');
    const result = run('--skills-dir', root);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /Refusing to overwrite/);
    assert.equal(await readFile(file, 'utf8'), 'user customization');
  } finally { await rm(root, { recursive: true, force: true }); }
});

test('refuses an existing destination symlink', async () => {
  const root = await mkdtemp(join(tmpdir(), 'groovectl-skill-test-'));
  try {
    const real = join(root, 'real');
    assert.equal(run('--skills-dir', real).status, 0);
    await symlink(join(real, 'groovectl'), join(root, 'groovectl'), process.platform === 'win32' ? 'junction' : 'dir');
    const result = run('--skills-dir', root);
    assert.equal(result.status, 1);
    await compareTrees(source, join(real, 'groovectl'));
  } finally { await rm(root, { recursive: true, force: true }); }
});

test('rejects malformed options and offers help without installing', () => {
  assert.equal(run('--unknown').status, 1);
  assert.equal(run('--skills-dir').status, 1);
  assert.equal(run('--skills-dir', '--help').status, 1);
  const result = run('--help');
  assert.equal(result.status, 0);
  assert.match(result.stdout, /not the groovectl CLI/);
});
