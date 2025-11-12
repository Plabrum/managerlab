import chokidar from 'chokidar';
import { spawn } from 'child_process';
import * as path from 'path';

const TEMPLATES_DIR = path.join(__dirname, '../templates');

console.log('👀 Watching for changes in email templates...\n');
console.log(`   Watching: ${TEMPLATES_DIR}/**/*.tsx`);
console.log(`   Auto-compiling to: ../templates/emails-react/\n`);

let isBuilding = false;
let queuedBuild = false;

function runBuild() {
  if (isBuilding) {
    queuedBuild = true;
    return;
  }

  isBuilding = true;
  console.log('🔨 Building templates...');

  const build = spawn('npm', ['run', 'build'], {
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit',
    shell: true,
  });

  build.on('close', (code) => {
    isBuilding = false;

    if (code === 0) {
      console.log('✓ Build complete\n');
    } else {
      console.error('✗ Build failed\n');
    }

    // If another change happened during build, run again
    if (queuedBuild) {
      queuedBuild = false;
      setTimeout(runBuild, 100);
    }
  });
}

// Initial build
runBuild();

// Watch for changes
const watcher = chokidar.watch(`${TEMPLATES_DIR}/**/*.tsx`, {
  ignored: /(^|[\/\\])\../, // ignore dotfiles
  persistent: true,
  ignoreInitial: true,
});

watcher
  .on('change', (filePath) => {
    console.log(`📝 Changed: ${path.relative(process.cwd(), filePath)}`);
    runBuild();
  })
  .on('add', (filePath) => {
    console.log(`➕ Added: ${path.relative(process.cwd(), filePath)}`);
    runBuild();
  })
  .on('unlink', (filePath) => {
    console.log(`➖ Removed: ${path.relative(process.cwd(), filePath)}`);
    runBuild();
  });

// Handle cleanup
process.on('SIGINT', () => {
  console.log('\n\n👋 Stopping watch mode...');
  watcher.close();
  process.exit(0);
});
