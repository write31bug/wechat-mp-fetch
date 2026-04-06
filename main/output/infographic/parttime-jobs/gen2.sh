#!/bin/bash
PROMPT="Clean white infographic poster with 4 colorful cards in 2x2 grid layout. Each card has a large numbered circle (1,2,3,4) at top, below it an icon representing job type (clock for daily, calendar for weekly, calendar-month for monthly, sun-snow for seasonal). Each card has labeled sections with dotted placeholder lines where text would go. Cards have soft pastel colors: blue, green, orange, purple. Title area at top center. Professional educational infographic style, no text, only visual placeholders."
OUT="/e/openclaw-work/infographic/parttime-jobs/bg.png"
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
