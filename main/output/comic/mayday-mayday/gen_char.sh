#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
PROMPT="Character reference sheet manga style. Six Chinese characters labeled with Chinese names: 叙述者我 ordinary young person watching phone excited casual clothes. 阿泽 male mid-20s warm big brother casual hoodie smile Shenyang. 小鱼 female 20s gentle student with glasses sweater Wuhan loves writing. 老王 male early 30s architecture industry calm rational button-up shirt Guangzhou. 小北 non-binary young artistic musician messy hair denim jacket creative Chengdu. 婷婷 female late 20s warm caring office worker neat blouse kind smile Beijing. Japanese manga style clean lineart flat colors warm pastel tones white background. All Asian features looking friendly and warm. Chinese name labels below each character."
OUT="/e/openclaw-work/comic/mayday-mayday/characters/characters.png"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
