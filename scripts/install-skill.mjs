#!/usr/bin/env node
import { cp, mkdir, rm } from 'node:fs/promises';
import { homedir } from 'node:os';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const usage = `Install only the groovectl skill (not the groovectl CLI).
Usage: node scripts/install-skill.mjs [--skills-dir <directory>]
Default: ~/.agents/skills/groovectl
Existing destinations are never overwritten. To update, back up and remove
the old groovectl skill directory yourself, then run this installer again.`;

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 1 && ['--help', '-h'].includes(args[0])) {
    console.log(usage);
    return;
  }
  if (args.length !== 0 && !(args.length === 2 && args[0] === '--skills-dir' && args[1] && !args[1].startsWith('--'))) {
    throw new Error(usage);
  }
  if (Number(process.versions.node.split('.')[0]) < 24) {
    throw new Error('Node.js 24 or newer is required. See README.md, step 1.');
  }
  const root = args.length === 2 ? resolve(args[1]) : join(homedir(), '.agents', 'skills');
  const target = join(root, 'groovectl');
  const source = fileURLToPath(new URL('../skills/groovectl', import.meta.url));
  await mkdir(root, { recursive: true });
  try {
    await mkdir(target);
  } catch (error) {
    if (error.code === 'EEXIST') throw new Error(`Refusing to overwrite existing destination: ${target}`);
    throw error;
  }
  try {
    await cp(source, target, { recursive: true, errorOnExist: true, force: false });
  } catch (error) {
    await rm(target, { recursive: true, force: true });
    throw error;
  }
  console.log(`Installed skill: ${target}`);
  console.log('CLI installation is separate: npm install --global groovectl@0.2.0');
  console.log('Verify: groovectl version --json && groovectl schema --compact; then ask Codex to use $groovectl.');
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
