#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
PROMPT="Minimalist corporate infographic background 3:4 portrait. Clean white canvas with colorful flat design elements. Bento grid layout with rounded rectangle blocks in soft pastel colors: light blue, mint green, coral, lavender. Each block has subtle gradient and soft drop shadow. Plenty of white space for text. Abstract decorative elements: tiny stars, dots, simple geometric shapes scattered. Modern clean corporate memphis style, flat illustration, no text, no people icons. Professional recruitment poster aesthetic. High quality."
OUT="/e/openclaw-work/infographic/job-ad/bg.png"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
