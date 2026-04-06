#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
OUT="/e/openclaw-work/infographic/tmp_article.png"
npx -y bun "$SKILL" --prompt "A screenshot or readable content of WeChat public account article. The page shows an article from a public account called Seaborg的自留地. The article title appears to be about someone named 对手. This is just a reference screenshot for context." --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
