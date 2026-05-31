const fs = require('fs');

const configPath = 'src/config.py';
let content = fs.readFileSync(configPath, 'utf8');

// Replace the LLM_PRESETS block with dynamic extraction
const regex = /LLM_PRESETS = \{[\s\S]*?\}/;
const newContent = `CUSTOM_BASE_URL = os.environ.get("CUSTOM_BASE_URL", "")`;

content = content.replace(regex, newContent);

fs.writeFileSync(configPath, content);
console.log("Successfully patched config.py");
