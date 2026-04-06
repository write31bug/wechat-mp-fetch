#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
PROMPT="Meme poster style. A person sitting at desk in dark room late at night, completely absorbed and obsessed staring at laptop screen glowing with OpenClaw AI assistant interface. Coffee cups everywhere, messy hair, wide excited eyes reflecting the screen glow, earphones in. The laptop shows glowing orange OpenClaw logo. Surrounded by sticky notes and tasks. Time shown as 3AM on clock. Humorous comedy style, meme format, dark cozy lighting, orange glow from screen illuminating face."
OUT="/e/openclaw-work/meme-openclaw/bg.png"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
