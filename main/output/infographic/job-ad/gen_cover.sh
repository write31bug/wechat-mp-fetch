#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
PROMPT="Corporate recruitment poster cover image, 3:4 portrait. Bold typography centered: 星光科技 2026春季招聘 in large white text. Background: deep blue to purple gradient night sky with scattered glowing stars. Abstract flat illustration of diverse young professionals sitting together in casual office pose, warm and friendly atmosphere. Floating recruitment icons: chat bubbles, code brackets, design tools. Bottom tagline in Chinese: 做热爱的事，和对味的人. Clean white recruitment badge icon top right corner. Corporate memphis flat vector style, warm inviting mood, professional yet approachable aesthetic."
OUT="/e/openclaw-work/infographic/job-ad/cover.png"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
