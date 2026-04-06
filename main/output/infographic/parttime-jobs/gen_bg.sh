#!/bin/bash
PROMPT="Minimalist abstract infographic background, 3:4 portrait. Four soft pastel gradient color blocks arranged in 2x2 grid layout. Colors: soft blue top-left, soft green top-right, soft orange bottom-left, soft purple bottom-right. Each block has rounded corners, gentle gradient from top-left to bottom-right. Large white clean areas between blocks for placing text. Subtle drop shadows between cards. Clean white background overall. Modern flat design, no text, no people, no icons. High resolution, professional design."
OUT="/e/openclaw-work/infographic/parttime-jobs/bg_clean.png"
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --ar "3:4" --provider dashscope --model qwen-image-2.0-pro --quality 2k
