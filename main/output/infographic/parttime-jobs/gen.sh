#!/bin/bash
PROMPT="兼职类型对比信息图，4种兼职类型卡片式对比布局"
OUT="/e/openclaw-work/infographic/parttime-jobs/result.png"
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
