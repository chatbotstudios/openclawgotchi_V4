import readline from 'readline';

function showMenu(options) {
  return new Promise((resolve) => {
    process.stdout.write("Menu:\n");
    let currentIndex = 0;

    function onKeyData(chunk) {
      const str = chunk.toString();
      if (str === '\u001b[A') currentIndex--;
      if (str === '\u001b[B') currentIndex++;
      console.log('got:', JSON.stringify(str));
      if (str === '\r' || str === '\n') {
        process.stdin.removeListener('data', onKeyData);
        resolve(options[currentIndex]);
      } else if (str === '\u0003') {
        process.exit(0);
      }
    }
    process.stdin.on('data', onKeyData);
  });
}

function askQuestion(promptText) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    rl.question(promptText + ': ', (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function main() {
  if (process.stdin.isTTY) process.stdin.setRawMode(true);
  
  const res1 = await showMenu(['a', 'b']);
  console.log('chosen:', res1);

  if (process.stdin.isTTY) process.stdin.setRawMode(false);
  const res2 = await askQuestion('name');
  console.log('name:', res2);
  
  if (process.stdin.isTTY) process.stdin.setRawMode(true);
  const res3 = await showMenu(['c', 'd']);
  console.log('chosen:', res3);
  
  process.exit(0);
}

main();
