#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Retry page 4..."
npx -y bun "$SKILL" --prompt "Manga comic page 4 of 6, 3:4 portrait. Four panel split showing four males pretending to be confused and making excuses. Panel 1: young male looking at phone pretending bad signal saying 信号不好. Panel 2: another male acting like he did not hear asking 什么？再说一遍？ Panel 3: third male saying 嗯？网卡了 不好意思. Panel 4: fourth male doing peace sign awkward smile saying 在吗？ Japanese manga comedy style, exaggerated expressions, clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p04.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Done p4"
