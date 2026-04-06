#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
npx -y bun "$SKILL" --prompt "Dark manga ending, 3:4 portrait. Pitch black dark room, person sitting alone in darkness. Only two glowing orange lobster eyes visible in computer monitor in front. Narration text: 我会永远在那里. 三秒内回复. 永远秒回. Ominous peaceful horror ending. Dark atmospheric manga, glowing lobster eyes in darkness, terrifying silence, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p07.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k
