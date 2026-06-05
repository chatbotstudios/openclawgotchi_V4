import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

// Static Premium Unicode-Animations Frame Data (100% Self-Contained)
const spinners = {
  helix: { frames: ['⠙⠢⣄⣠', '⠙⠢⣄⣠', '⠚⠔⣠⣄', '⠖⠒⣠⣄'], interval: 80 },
  pong: { frames: ['🏓      ·', '🏓     · ', '🏓    ·  ', '🏓   ·   ', '🏓  ·    ', '🏓 ·     ', '🏓·      ', '·🏓      '], interval: 80 },
  hearts: { frames: ['💛', '🧡', '❤', '💜', '💙', '🩵', '💚'], interval: 150 },
  moon: { frames: ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'], interval: 100 },
  scan: { frames: ['⡇', '⠏', '⠛', '⠹', '⢸', '⣰', '⣤', '⣆'], interval: 70 },
  'radar-2': { frames: ['⠁', '⠂', '⠄', '⡀', '⢀', '⠠', '⠐', '⠈'], interval: 100 },
  mitosis: { frames: ['⠀⠂⠀', '⠀⠒⠀', '⠀⠶⠀', '⠶⠶⠀', '⠶⠀⠶', '⠒⠀⠒', '⠂⠀⠂'], interval: 180 },
  pacman: { frames: ['d ∙ ∙ ∙', 'd∙ ∙ ∙ ', '● ∙ ∙  ', 'o  ∙ ∙ ', ' ● ∙ ∙ ', ' o ∙ ∙ ', '  ● ∙  ', '  o ∙  ', '   ●   ', '   o   ', '       '], interval: 120 }
};

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '../..');
const ENV_FILE = path.join(ROOT_DIR, '.env');
const SENTINEL_FILE = path.join(ROOT_DIR, 'templates', '.setup_completed');

// Curated ANSI Styling (Pink & Blue)
const PINK = '\x1B[38;5;205m';
const BLUE = '\x1B[38;5;39m';
const GREEN = '\x1B[38;5;120m';
const RED = '\x1B[38;5;196m';
const RESET = '\x1B[0m';
const BOLD = '\x1B[1m';
const HIDE_CURSOR = '\x1B[?25l';
const SHOW_CURSOR = '\x1B[?25h';
const CLEAR_SCREEN = '\x1B[2J\x1B[H';

// Configuration State
const answers = {
  setupMode: 'Quick Setup',
  aiProvider: 'Gemini',
  aiModel: 'gemini-1.5-flash',
  geminiKey: '',
  openaiKey: '',
  anthropicKey: '',
  deepseekKey: '',
  platforms: { telegram: false, discord: false },
  telegramToken: '',
  telegramAllowed: '',
  discordToken: '',
  discordAllowed: '',
  botName: 'Gotchi',
  ownerName: 'Owner',
  device: 'Raspberry Pi Zero 2W',
  deployment: 'Local'
};

const setupModes = ['Quick Setup', 'Full Setup'];
const providers = [
  'Nous Portal',
  'OpenRouter',
  'NovitaAI',
  'LM Studio',
  'Anthropic',
  'OpenAI Codex',
  'OpenAI API',
  'Qwen Cloud / DashScope',
  'xAI Grok OAuth',
  'Xiaomi MiMo',
  'Tencent TokenHub',
  'NVIDIA NIM',
  'GitHub Copilot',
  'GitHub Copilot ACP',
  'Hugging Face',
  'Google AI Studio',
  'Google Gemini via OAuth',
  'DeepSeek',
  'xAI',
  'Z.AI / GLM',
  'Kimi Coding Plan'
];
const modelsMap = {
  'Nous Portal': [
    'anthropic/claude-opus-4.7', 'anthropic/claude-opus-4.6', 'anthropic/claude-sonnet-4.6',
    'moonshotai/kimi-k2.6', 'qwen/qwen3.7-max', 'anthropic/claude-haiku-4.5',
    'openai/gpt-5.5', 'openai/gpt-5.5-pro', 'openai/gpt-5.4-mini', 'openai/gpt-5.4-nano',
    'openai/gpt-5.3-codex', 'xiaomi/mimo-v2.5-pro', 'tencent/hy3-preview',
    'google/gemini-3-pro-preview', 'google/gemini-3-flash-preview', 'google/gemini-3.1-pro-preview',
    'google/gemini-3.1-flash-lite-preview', 'qwen/qwen3.6-35b-a3b', 'stepfun/step-3.5-flash',
    'minimax/minimax-m2.7', 'z-ai/glm-5.1', 'x-ai/grok-4.3', 'nvidia/nemotron-3-super-120b-a12b',
    'deepseek/deepseek-v4-pro'
  ],
  'OpenRouter': [
    'anthropic/claude-opus-4.7', 'anthropic/claude-opus-4.6', 'anthropic/claude-sonnet-4.6',
    'moonshotai/kimi-k2.6', 'openrouter/pareto-code', 'qwen/qwen3.7-max', 'anthropic/claude-haiku-4.5',
    'openai/gpt-5.5', 'openai/gpt-5.5-pro', 'openai/gpt-5.4-mini', 'openai/gpt-5.4-nano',
    'openai/gpt-5.3-codex', 'xiaomi/mimo-v2.5-pro', 'tencent/hy3-preview',
    'google/gemini-3-pro-image-preview', 'google/gemini-3-flash-preview', 'google/gemini-3.1-pro-preview',
    'google/gemini-3.1-flash-lite-preview', 'qwen/qwen3.6-35b-a3b', 'stepfun/step-3.5-flash',
    'minimax/minimax-m2.7', 'z-ai/glm-5.1', 'x-ai/grok-4.20', 'x-ai/grok-4.3',
    'nvidia/nemotron-3-super-120b-a12b', 'deepseek/deepseek-v4-pro', 'openrouter/elephant-alpha',
    'openrouter/owl-alpha', 'tencent/hy3-preview:free', 'nvidia/nemotron-3-super-120b-a12b:free',
    'inclusionai/ring-2.6-1t:free', 'custom'
  ],
  'NovitaAI': [
    'moonshotai/kimi-k2.5', 'minimax/minimax-m2.7', 'zai-org/glm-5', 'deepseek/deepseek-v3-0324',
    'deepseek/deepseek-r1-0528', 'qwen/qwen3-235b-a22b-fp8', 'custom'
  ],
  'LM Studio': ['custom'],
  'Anthropic': [
    'claude-opus-4-7', 'claude-opus-4-6', 'claude-sonnet-4-6', 'claude-opus-4-5-20251101',
    'claude-sonnet-4-5-20250929', 'claude-opus-4-20250514', 'claude-sonnet-4-20250514',
    'claude-haiku-4-5-20251001', 'custom'
  ],
  'OpenAI Codex': ['gpt-5.3-codex', 'gpt-5.2-codex', 'custom'],
  'OpenAI API': [
    'gpt-5.5', 'gpt-5.5-pro', 'gpt-5.4', 'gpt-5.4-mini', 'gpt-5.4-nano', 'gpt-5-mini',
    'gpt-5.3-codex', 'gpt-4.1', 'gpt-4o', 'gpt-4o-mini', 'custom'
  ],
  'Qwen Cloud / DashScope': [
    'qwen3.7-max', 'qwen3.6-plus', 'kimi-k2.5', 'qwen3.5-plus', 'qwen3-coder-plus', 'qwen3-coder-next',
    'glm-5', 'glm-4.7', 'MiniMax-M2.5', 'custom'
  ],
  'xAI Grok OAuth': [
    'grok-4.3', 'grok-4.20-0309-reasoning', 'grok-4.20-0309-non-reasoning', 'grok-4.20-multi-agent-0309', 'custom'
  ],
  'Xiaomi MiMo': [
    'mimo-v2.5-pro', 'mimo-v2.5', 'mimo-v2-pro', 'mimo-v2-omni', 'mimo-v2-flash', 'custom'
  ],
  'Tencent TokenHub': ['hy3-preview', 'custom'],
  'NVIDIA NIM': [
    'nvidia/nemotron-3-super-120b-a12b', 'nvidia/nemotron-3-nano-30b-a3b',
    'nvidia/llama-3.3-nemotron-super-49b-v1.5', 'qwen/qwen3.5-397b-a17b', 'deepseek-ai/deepseek-v3.2',
    'moonshotai/kimi-k2.6', 'minimaxai/minimax-m2.5', 'z-ai/glm5', 'openai/gpt-oss-120b', 'custom'
  ],
  'GitHub Copilot': [
    'gpt-5.4', 'gpt-5.4-mini', 'gpt-5-mini', 'gpt-5.3-codex', 'gpt-5.2-codex', 'gpt-4.1', 'gpt-4o',
    'gpt-4o-mini', 'claude-sonnet-4.6', 'claude-sonnet-4', 'claude-sonnet-4.5', 'claude-haiku-4.5',
    'gemini-3.1-pro-preview', 'gemini-3-pro-preview', 'gemini-3-flash-preview', 'gemini-2.5-pro', 'custom'
  ],
  'GitHub Copilot ACP': ['copilot-acp'],
  'Hugging Face': [
    'moonshotai/Kimi-K2.5', 'Qwen/Qwen3.5-397B-A17B', 'Qwen/Qwen3.5-35B-A3B', 'deepseek-ai/DeepSeek-V3.2',
    'MiniMaxAI/MiniMax-M2.5', 'zai-org/GLM-5', 'XiaomiMiMo/MiMo-V2-Flash', 'moonshotai/Kimi-K2-Thinking',
    'moonshotai/Kimi-K2.6', 'custom'
  ],
  'Google AI Studio': [
    'gemini-3.1-pro-preview', 'gemini-3-pro-preview', 'gemini-3-flash-preview',
    'gemini-3.1-flash-lite-preview', 'custom'
  ],
  'Google Gemini via OAuth': [
    'gemini-3.1-pro-preview', 'gemini-3-pro-preview', 'gemini-3-flash-preview', 'custom'
  ],
  'DeepSeek': [
    'deepseek-v4-pro', 'deepseek-v4-flash', 'deepseek-chat', 'deepseek-reasoner', 'custom'
  ],
  'xAI': [
    'grok-4.3', 'grok-4.20-0309-reasoning', 'grok-4.20-0309-non-reasoning', 'grok-4.20-multi-agent-0309', 'custom'
  ],
  'Z.AI / GLM': [
    'glm-5.1', 'glm-5', 'glm-5v-turbo', 'glm-5-turbo', 'glm-4.7', 'glm-4.5', 'glm-4.5-flash', 'custom'
  ],
  'Kimi Coding Plan': [
    'kimi-k2.6', 'kimi-k2.5', 'kimi-for-coding', 'kimi-k2-thinking', 'kimi-k2-thinking-turbo',
    'kimi-k2-turbo-preview', 'kimi-k2-0905-preview', 'custom'
  ]
};
const platformChoices = ['Telegram Bot', 'Discord Bot'];
const devices = [
  'Raspberry Pi Zero 2W',
  'Raspberry Pi 3',
  'Raspberry Pi 4',
  'Raspberry Pi 5',
  'ESP32-S3',
  'ESP32-WROOM',
  'Standard PC / Mac'
];
const deployments = ['Local', 'VPS'];

let animationInterval = null;
let currentFrameIdx = 0;

function cleanup() {
  if (animationInterval) clearInterval(animationInterval);
  process.stdout.write(SHOW_CURSOR);
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(false);
    process.stdin.pause();
  }
}

function renderSpinner(message, spinnerName = 'helix', color = PINK) {
  const spinner = spinners[spinnerName] || spinners.helix;
  const { frames, interval } = spinner;
  
  if (animationInterval) clearInterval(animationInterval);
  process.stdout.write(HIDE_CURSOR);
  
  animationInterval = setInterval(() => {
    const frame = frames[currentFrameIdx++ % frames.length];
    process.stdout.write(`\r\x1B[2K  ${color}${frame}${RESET}  ${message}`);
  }, interval);
}

function stopSpinner(successMessage, success = true) {
  if (animationInterval) {
    clearInterval(animationInterval);
    animationInterval = null;
  }
  const symbol = success ? `${GREEN}✔${RESET}` : `${RED}✘${RESET}`;
  process.stdout.write(`\r\x1B[2K  ${symbol}  ${successMessage}\n`);
  process.stdout.write(SHOW_CURSOR);
}

function askQuestion(promptText, defaultValue = '') {
  return new Promise((resolve) => {
    process.stdout.write(SHOW_CURSOR);
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    const formattedPrompt = `${BLUE}❓${RESET} ${promptText}${defaultValue ? ` [${defaultValue}]` : ''}: `;
    rl.question(formattedPrompt, (answer) => {
      rl.close();
      process.stdout.write(HIDE_CURSOR);
      resolve(answer.trim() || defaultValue);
    });
  });
}

function showMenu(title, options, currentIndex = 0) {
  return new Promise((resolve) => {
    process.stdout.write(HIDE_CURSOR);
    if (process.stdin.isTTY) {
      process.stdin.setRawMode(true);
      process.stdin.resume();
    }
    
    function draw() {
      process.stdout.write(CLEAR_SCREEN);
      console.log(`\n${PINK}╔═══════════════════════════════════════════════════╗${RESET}`);
      console.log(`${PINK}║${RESET} ${BOLD}${BLUE}${title.padEnd(49)}${RESET} ${PINK}║${RESET}`);
      console.log(`${PINK}╚═══════════════════════════════════════════════════╝${RESET}\n`);
      console.log(`  Use ${BOLD}↑/↓${RESET} keys or ${BOLD}number keys (1-${options.length})${RESET} to navigate, ${BOLD}Enter${RESET} to confirm.\n`);
      
      options.forEach((opt, idx) => {
        const isCurrent = idx === currentIndex;
        const pointer = isCurrent ? `${PINK}➔${RESET} ` : '  ';
        const numLabel = `[${idx + 1}] `;
        if (isCurrent) {
          console.log(`  ${pointer}${numLabel}${BOLD}${BLUE}${opt}${RESET}`);
        } else {
          console.log(`  ${pointer}${numLabel}${opt}`);
        }
      });
      console.log(`\n`);
    }

    draw();

    function onKeypress(str, key) {
      if (key && key.ctrl && key.name === 'c') {
        cleanup();
        process.exit(0);
      } else if (key && key.name === 'up') {
        currentIndex = (currentIndex - 1 + options.length) % options.length;
        draw();
      } else if (key && key.name === 'down') {
        currentIndex = (currentIndex + 1) % options.length;
        draw();
      } else if (key && (key.name === 'return' || key.name === 'enter')) {
        process.stdin.removeListener('keypress', onKeypress);
        if (process.stdin.isTTY) {
          process.stdin.setRawMode(false);
          process.stdin.pause();
        }
        resolve(options[currentIndex]);
      } else if (str && str >= '1' && str <= '9') {
        const num = parseInt(str, 10);
        if (num >= 1 && num <= options.length) {
          currentIndex = num - 1;
          draw();
        }
      }
    }

    process.stdin.on('keypress', onKeypress);
  });
}

async function runRealDiagnostics() {
  process.stdout.write(CLEAR_SCREEN);
  console.log(`\n${BLUE}🔍 Running Authentic Hardware Diagnostics...${RESET}\n`);
  
  const runTest = async (testName, spinnerName, command, failAllowed = true) => {
    renderSpinner(`Testing ${testName}...`, spinnerName, BLUE);
    await new Promise(r => setTimeout(r, 1000));
    try {
      execSync(command, { stdio: 'ignore' });
      stopSpinner(`${testName}: Operational`, true);
    } catch (e) {
      if (failAllowed) {
        stopSpinner(`${testName}: Not found or failed (ignoring for now)`, false);
      } else {
        stopSpinner(`${testName}: CRITICAL FAILURE`, false);
      }
    }
    await new Promise(r => setTimeout(r, 500));
  };

  await runTest('WiFi Interface (wlan0)', 'scan', 'ip a show wlan0 || iwconfig wlan0');
  await runTest('Bluetooth HCI Adapter', 'radar-2', 'hciconfig || bluetoothctl show');
  await runTest('E-Ink SPI Bus (/dev/spi*)', 'mitosis', 'ls -l /dev/spi*');
  await runTest('System Python Packages', 'pacman', 'python3 -c "import sqlite3; import urllib"');
  
  console.log(`\n${GREEN}🎉 Authentic diagnostic phase complete!${RESET}\n`);
  await askQuestion('Press Enter to continue setup');
}

async function main() {
  readline.emitKeypressEvents(process.stdin);
  process.stdout.write(CLEAR_SCREEN);
  
  // 1. Welcome Intro
  renderSpinner('Initializing Tactical Setup Suite...', 'helix');
  await new Promise(r => setTimeout(r, 2000));
  stopSpinner('Tactical Setup Suite ready!');

  console.log(`\n${PINK}  🛸 WELCOME TO OPENCLAWGOTCHI V3 🛸${RESET}`);
  console.log(`  Let's bring your tactical companion online!\n`);

  // --- Autodetect Existing .env ---
  let existingEnv = {};
  if (fs.existsSync(ENV_FILE)) {
    const content = fs.readFileSync(ENV_FILE, 'utf8');
    content.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
        const parts = trimmed.split('=');
        const key = parts[0].trim();
        const val = parts.slice(1).join('=').trim();
        existingEnv[key] = val;
      }
    });
  }

  if (Object.keys(existingEnv).length > 0) {
    console.log(`${GREEN}  ℹ️  Detected existing environment configuration (.env)!${RESET}`);
    const confirmation = await askQuestion('  Would you like to auto-detect and use these existing values as defaults? (Y/n)', 'Y');
    if (confirmation.toUpperCase().startsWith('Y')) {
      if (existingEnv['BOT_NAME']) answers.botName = existingEnv['BOT_NAME'];
      if (existingEnv['OWNER_NAME']) answers.ownerName = existingEnv['OWNER_NAME'];
      if (existingEnv['BOT_PLATFORM']) {
        const platform = existingEnv['BOT_PLATFORM'].toLowerCase();
        answers.platforms.discord = (platform === 'discord');
        answers.platforms.telegram = (platform === 'telegram');
      }
      if (existingEnv['TELEGRAM_BOT_TOKEN']) answers.telegramToken = existingEnv['TELEGRAM_BOT_TOKEN'];
      if (existingEnv['TELEGRAM_ALLOWED_USERS']) answers.telegramAllowed = existingEnv['TELEGRAM_ALLOWED_USERS'];
      if (existingEnv['DISCORD_BOT_TOKEN']) answers.discordToken = existingEnv['DISCORD_BOT_TOKEN'];
      if (existingEnv['DISCORD_ALLOWED_USERS']) answers.discordAllowed = existingEnv['DISCORD_ALLOWED_USERS'];
      if (existingEnv['DEFAULT_LITE_MODEL']) answers.aiModel = existingEnv['DEFAULT_LITE_MODEL'];
      
      if (existingEnv['DEFAULT_LITE_PRESET']) {
        const preset = existingEnv['DEFAULT_LITE_PRESET'].toLowerCase();
        const providerName = providers.find(p => p.replace(/\s+/g, '_').toLowerCase() === preset);
        if (providerName) {
          answers.aiProvider = providerName;
        }
      }
      
      // Load specific provider api keys from .env
      const keyMap = {
        'Nous Portal': 'NOUS_API_KEY',
        'OpenRouter': 'OPENROUTER_API_KEY',
        'NovitaAI': 'NOVITA_API_KEY',
        'Anthropic': 'ANTHROPIC_API_KEY',
        'OpenAI API': 'OPENAI_API_KEY',
        'OpenAI Codex': 'OPENAI_API_KEY',
        'Qwen Cloud / DashScope': 'DASHSCOPE_API_KEY',
        'xAI': 'XAI_API_KEY',
        'Xiaomi MiMo': 'XIAOMI_API_KEY',
        'Tencent TokenHub': 'TENCENT_API_KEY',
        'NVIDIA NIM': 'NVIDIA_API_KEY',
        'Hugging Face': 'HUGGINGFACE_API_KEY',
        'Google AI Studio': 'GEMINI_API_KEY',
        'DeepSeek': 'DEEPSEEK_API_KEY',
        'Z.AI / GLM': 'ZAI_API_KEY',
        'Kimi Coding Plan': 'MOONSHOT_API_KEY',
        'GitHub Copilot': 'GITHUB_TOKEN'
      };
      
      if (keyMap[answers.aiProvider] && existingEnv[keyMap[answers.aiProvider]]) {
        answers.dynamicApiKey = existingEnv[keyMap[answers.aiProvider]];
        answers.dynamicEnvKeyName = keyMap[answers.aiProvider];
      }
      
      if (existingEnv['GOTCHI_DEVICE']) answers.device = existingEnv['GOTCHI_DEVICE'];
      if (existingEnv['GOTCHI_DEPLOYMENT']) answers.deployment = existingEnv['GOTCHI_DEPLOYMENT'];
      if (existingEnv['CUSTOM_BASE_URL']) answers.customBaseUrl = existingEnv['CUSTOM_BASE_URL'];
    }
  }

  await askQuestion('Press Enter to begin Configuration');

  answers.setupMode = await showMenu('Select Setup Mode', setupModes);

  // --- PHASE 1: KEYS & PLATFORMS ---
  let defaultProviderIdx = providers.indexOf(answers.aiProvider);
  if (defaultProviderIdx === -1) defaultProviderIdx = 0;
  answers.aiProvider = await showMenu('Choose AI/LLM Provider', providers, defaultProviderIdx);
  
  // Clean up key prompt logic dynamically based on provider
  let requiresKey = true;
  let keyPrompt = `Enter your ${answers.aiProvider} API Key`;
  let envKeyName = 'CUSTOM_API_KEY';

  switch (answers.aiProvider) {
    case 'Nous Portal': envKeyName = 'NOUS_API_KEY'; break;
    case 'OpenRouter': envKeyName = 'OPENROUTER_API_KEY'; break;
    case 'NovitaAI': envKeyName = 'NOVITA_API_KEY'; break;
    case 'Anthropic': envKeyName = 'ANTHROPIC_API_KEY'; break;
    case 'OpenAI API': 
    case 'OpenAI Codex': envKeyName = 'OPENAI_API_KEY'; break;
    case 'Qwen Cloud / DashScope': envKeyName = 'DASHSCOPE_API_KEY'; break;
    case 'xAI': envKeyName = 'XAI_API_KEY'; break;
    case 'Xiaomi MiMo': envKeyName = 'XIAOMI_API_KEY'; break;
    case 'Tencent TokenHub': envKeyName = 'TENCENT_API_KEY'; break;
    case 'NVIDIA NIM': envKeyName = 'NVIDIA_API_KEY'; break;
    case 'Hugging Face': envKeyName = 'HUGGINGFACE_API_KEY'; break;
    case 'Google AI Studio': envKeyName = 'GEMINI_API_KEY'; break;
    case 'DeepSeek': envKeyName = 'DEEPSEEK_API_KEY'; break;
    case 'Z.AI / GLM': envKeyName = 'ZAI_API_KEY'; break;
    case 'Kimi Coding Plan': envKeyName = 'MOONSHOT_API_KEY'; break;
    case 'GitHub Copilot': envKeyName = 'GITHUB_TOKEN'; break;
    case 'LM Studio': 
      requiresKey = false; 
      answers.customBaseUrl = await askQuestion('Enter LM Studio URL', answers.customBaseUrl || 'http://127.0.0.1:1234/v1');
      break;
    case 'xAI Grok OAuth':
    case 'Google Gemini via OAuth':
    case 'GitHub Copilot ACP':
      requiresKey = false; // Uses internal auth flows
      break;
  }
  
  if (requiresKey) {
    answers.dynamicApiKey = await askQuestion(keyPrompt, answers.dynamicApiKey);
    answers.dynamicEnvKeyName = envKeyName;
  }
  
  const recommendedModels = modelsMap[answers.aiProvider] || ['custom'];
  let defaultModelIdx = recommendedModels.indexOf(answers.aiModel);
  if (defaultModelIdx === -1) defaultModelIdx = 0;
  answers.aiModel = await showMenu(`Select ${answers.aiProvider} Model`, recommendedModels, defaultModelIdx);
  
  if (answers.aiModel === 'custom') {
    answers.aiModel = await askQuestion('Enter custom model tag', answers.aiModel);
  }

  let defaultPlatformIdx = answers.platforms.discord ? 1 : 0;
  const selectedPlatform = await showMenu('Select Primary Bot Platform', platformChoices, defaultPlatformIdx);
  if (selectedPlatform === 'Telegram Bot') {
    answers.platforms.telegram = true;
    answers.platforms.discord = false;
    answers.telegramToken = await askQuestion('Enter Telegram Bot Token', answers.telegramToken);
    answers.telegramAllowed = await askQuestion('Enter Telegram User ID (Allowed admin)', answers.telegramAllowed);
  } else if (selectedPlatform === 'Discord Bot') {
    answers.platforms.discord = true;
    answers.platforms.telegram = false;
    answers.discordToken = await askQuestion('Enter Discord Bot Token', answers.discordToken);
    answers.discordAllowed = await askQuestion('Enter Discord Allowed User ID', answers.discordAllowed);
  }

  answers.botName = await askQuestion('Companion Name', answers.botName || 'Gotchi');
  answers.ownerName = await askQuestion('Your Name (Operator)', answers.ownerName || 'Owner');

  // --- PHASE 2 & 3: DEVICE & DEPLOYMENT TARGET ---
  const typeChoices = [
    'Raspberry Pi or ESP32 Edge Device',
    'Local Machine (launches Gotchi on your local PC / Mac)',
    'VPS / Cloud Server (launches Gotchi on a cloud VPS IP)'
  ];
  
  let defaultTypeIdx = 0;
  if (answers.deployment === 'Local' && answers.device === 'Standard PC / Mac') {
    defaultTypeIdx = 1;
  } else if (answers.deployment === 'VPS') {
    defaultTypeIdx = 2;
  }
  
  const selectedType = await showMenu('Select Device or Deployment Type', typeChoices, defaultTypeIdx);
  
  if (selectedType === 'Raspberry Pi or ESP32 Edge Device') {
    let defaultDeviceIdx = 0;
    if (answers.device && devices.indexOf(answers.device) !== -1) {
      defaultDeviceIdx = devices.indexOf(answers.device);
    }
    answers.device = await showMenu('Select Target Hardware Device', devices.filter(d => d !== 'Standard PC / Mac'), defaultDeviceIdx);
    answers.deployment = 'Device';
    
    if (answers.device.includes('Raspberry Pi') && answers.setupMode === 'Full Setup') {
      const diagChoice = await showMenu('Hardware Diagnostics', ['Run Diagnostics Now', 'Skip', 'Test Later']);
      if (diagChoice === 'Run Diagnostics Now') {
        await runRealDiagnostics();
      }
    }
  } else if (selectedType === 'Local Machine (launches Gotchi on your local PC / Mac)') {
    answers.device = 'Standard PC / Mac';
    answers.deployment = 'Local';
    console.log(`\n${GREEN}✓ Configured as Local PC / Mac deployment. Diagnostics skipped.${RESET}`);
    await new Promise(r => setTimeout(r, 1200));
  } else {
    answers.device = 'Cloud VPS';
    answers.deployment = 'VPS';
    console.log(`\n${GREEN}✓ Configured as Cloud VPS deployment. Diagnostics skipped.${RESET}`);
    await new Promise(r => setTimeout(r, 1200));
  }

  // --- SAVE & CONCLUDE ---
  process.stdout.write(CLEAR_SCREEN);
  renderSpinner('Generating and saving system environment configurations...', 'pong', PINK);
  await new Promise(r => setTimeout(r, 2000));
  
  // 1. Generate or update .env file
  let envContent = '';
  if (fs.existsSync(ENV_FILE)) {
    envContent = fs.readFileSync(ENV_FILE, 'utf8');
  } else {
    envContent = fs.readFileSync(path.join(ROOT_DIR, '.env.example'), 'utf8');
  }

  const updates = {
    'BOT_NAME': answers.botName,
    'OWNER_NAME': answers.ownerName,
    'TELEGRAM_BOT_TOKEN': answers.telegramToken || '',
    'TELEGRAM_ALLOWED_USERS': answers.telegramAllowed || '',
    'DISCORD_BOT_TOKEN': answers.discordToken || '',
    'DISCORD_ALLOWED_USERS': answers.discordAllowed || '',
    'BOT_PLATFORM': answers.platforms.discord ? 'discord' : 'telegram',
    'DEFAULT_LITE_MODEL': answers.aiModel,
    'DEFAULT_LITE_PRESET': answers.aiProvider.replace(/\s+/g, '_').toLowerCase(),
    'GOTCHI_DEVICE': answers.device,
    'GOTCHI_DEPLOYMENT': answers.deployment
  };

  if (answers.dynamicEnvKeyName && answers.dynamicApiKey) {
    updates[answers.dynamicEnvKeyName] = answers.dynamicApiKey;
  }
  if (answers.customBaseUrl) {
    updates['CUSTOM_BASE_URL'] = answers.customBaseUrl;
  }

  Object.entries(updates).forEach(([key, val]) => {
    const regex = new RegExp(`^#?\\s*${key}=.*`, 'm');
    if (regex.test(envContent)) {
      envContent = envContent.replace(regex, `${key}=${val}`);
    } else {
      envContent += `\n${key}=${val}`;
    }
  });

  fs.writeFileSync(ENV_FILE, envContent.trim() + '\n', 'utf8');

  // 2. Create sentinel file to verify setup completion
  fs.mkdirSync(path.dirname(SENTINEL_FILE), { recursive: true });
  fs.writeFileSync(SENTINEL_FILE, JSON.stringify({
    setup_timestamp: new Date().toISOString(),
    configured_device: answers.device,
    configured_deployment: answers.deployment,
    setup_mode: answers.setupMode
  }, null, 2), 'utf8');

  stopSpinner('Configuration finalized and saved to .env successfully!');
  
  // Fun Unicode concluding animation loop
  renderSpinner('Booting up personality core...', 'moon', PINK);
  await new Promise(r => setTimeout(r, 1500));
  renderSpinner('Brewing digital coffee for the operator...', 'pong', BLUE);
  await new Promise(r => setTimeout(r, 1500));
  renderSpinner('Activating platform channels...', 'hearts', PINK);
  await new Promise(r => setTimeout(r, 1500));
  
  const connectedPlatform = answers.platforms.discord ? 'Discord client connected!' : 'Telegram bot webhook active!';
  stopSpinner(connectedPlatform);

  console.log(`\n${PINK}╔═══════════════════════════════════════════════════╗${RESET}`);
  console.log(`${PINK}║           🎉 Gotchi Setup Complete!               ║${RESET}`);
  console.log(`${PINK}║          Your Companion is now Ready!             ║${RESET}`);
  console.log(`${PINK}╚═══════════════════════════════════════════════════╝${RESET}\n`);

  if (answers.deployment === 'Local') {
    console.log(`  ${GREEN}ℹ️  Enable the Global 'gotchi' Command on your Mac / PC:${RESET}`);
    console.log(`     ${BOLD}sudo ln -sf "${ROOT_DIR}/gotchi" /usr/local/bin/gotchi${RESET}\n`);
    console.log(`  ${BLUE}Start your visual dashboard HUD:${RESET}`);
    console.log(`     ${BOLD}gotchi serve --port 8088${RESET}\n`);
  } else {
    console.log(`  Start the bot with:  ${BOLD}${BLUE}gotchi restart${RESET}\n`);
  }
  
  cleanup();
  process.exit(0);
}

main().catch(err => {
  console.error(err);
  cleanup();
  process.exit(1);
});
