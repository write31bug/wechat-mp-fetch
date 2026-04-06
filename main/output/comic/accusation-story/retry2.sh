#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Retry page 5..."
npx -y bun "$SKILL" --prompt "Manga comic page 5 of 6, 3:4 portrait. WeChat group chat screen filled with music links and album covers. Fov excitedly sending 周杰伦JayChou album covers and song links. 草莓园 sending G.E.M.邓紫棋 album covers. 钱总 watching speechless as chat fills up. Caption: 科普开始. Comedy manga style, phone screen filled with music emojis and streaming links, Japanese manga clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p05.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Done p5"
