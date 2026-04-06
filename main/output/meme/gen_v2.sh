#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

PROMPT="Meme poster style, dark moody scene. A cute bright orange cartoon lobster (OpenClaw mascot) sitting on a desk glowing triumphantly, radiating orange light. A person leaning in close with excited obsessed expression staring at the lobster, eyes wide with joy. Desk scene, late night, surrounded by coffee cups and sticky notes. The lobster mascot is center focus, large and charismatic, glowing with warm orange light. Comedy meme aesthetic, cartoon lobster character design, warm orange and dark contrast lighting. This is a parody meme celebrating how addictive the OpenClaw AI assistant is."
OUT="/e/openclaw-work/meme-openclaw/bg2.png"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
