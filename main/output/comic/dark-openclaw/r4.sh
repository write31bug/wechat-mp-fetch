#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
npx -y bun "$SKILL" --prompt "Dark manga horror, 3:4 portrait. Giant evil orange lobster crawling out of laptop screen. Lobster has sharp glowing red-orange eyes and evil grin. Dark room, ominous orange glow. Person at desk frozen in terror. Clean lineart flat colors horror manga style." --image "/e/openclaw-work/comic/dark-openclaw/p04.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k
