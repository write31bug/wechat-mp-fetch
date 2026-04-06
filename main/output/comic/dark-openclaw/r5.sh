#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
npx -y bun "$SKILL" --prompt "Dark manga, 3:4 portrait. Evil orange lobster standing on keyboard, glowing eyes, menacing smile, claws reaching toward viewer. Person backing away in fear. Dark room lit by orange screen glow. Ominous text: Token不够了. Horror manga style, dramatic lighting, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p05.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k
