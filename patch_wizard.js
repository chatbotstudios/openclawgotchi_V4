const fs = require('fs');

const wizardPath = 'src/cli/wizard.mjs';
let content = fs.readFileSync(wizardPath, 'utf8');

const newProviders = `const providers = [
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
];`;

const newModelsMap = `const modelsMap = {
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
};`;

// Replace `const providers = ...` and `const modelsMap = ...` in content
content = content.replace(/const providers = \[.*?\];/s, newProviders);
content = content.replace(/const modelsMap = \{.*?\};/s, newModelsMap);

// Replace phase 1 logic:
const phase1Regex = /\/\/ --- PHASE 1: KEYS & PLATFORMS ---.*?(?=const selectedPlatform = await showMenu)/s;
const newPhase1Logic = `// --- PHASE 1: KEYS & PLATFORMS ---
  answers.aiProvider = await showMenu('Choose AI/LLM Provider', providers);
  
  // Clean up key prompt logic dynamically based on provider
  let requiresKey = true;
  let keyPrompt = \`Enter your \${answers.aiProvider} API Key\`;
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
      answers.customBaseUrl = await askQuestion('Enter LM Studio URL', 'http://127.0.0.1:1234/v1');
      break;
    case 'xAI Grok OAuth':
    case 'Google Gemini via OAuth':
    case 'GitHub Copilot ACP':
      requiresKey = false; // Uses internal auth flows
      break;
  }
  
  if (requiresKey) {
    answers.dynamicApiKey = await askQuestion(keyPrompt);
    answers.dynamicEnvKeyName = envKeyName;
  }
  
  const recommendedModels = modelsMap[answers.aiProvider] || ['custom'];
  answers.aiModel = await showMenu(\`Select \${answers.aiProvider} Model\`, recommendedModels);
  
  if (answers.aiModel === 'custom') {
    answers.aiModel = await askQuestion('Enter custom model tag');
  }

  `;

content = content.replace(phase1Regex, newPhase1Logic);

// Replace env updates
const updatesRegex = /const updates = {[\s\S]*?};/s;
const newUpdatesLogic = `const updates = {
    'BOT_NAME': answers.botName,
    'OWNER_NAME': answers.ownerName,
    'TELEGRAM_BOT_TOKEN': answers.telegramToken,
    'TELEGRAM_ALLOWED_USERS': answers.telegramAllowed,
    'DISCORD_BOT_TOKEN': answers.discordToken,
    'DISCORD_ALLOWED_USERS': answers.discordAllowed,
    'BOT_PLATFORM': answers.platforms.discord ? 'discord' : 'telegram',
    'DEFAULT_LITE_MODEL': answers.aiModel,
    'DEFAULT_LITE_PRESET': answers.aiProvider.replace(/\\s+/g, '_').toLowerCase()
  };

  if (answers.dynamicEnvKeyName && answers.dynamicApiKey) {
    updates[answers.dynamicEnvKeyName] = answers.dynamicApiKey;
  }
  if (answers.customBaseUrl) {
    updates['CUSTOM_BASE_URL'] = answers.customBaseUrl;
  }`;
content = content.replace(updatesRegex, newUpdatesLogic);

fs.writeFileSync(wizardPath, content);
console.log("Successfully patched wizard.mjs");
