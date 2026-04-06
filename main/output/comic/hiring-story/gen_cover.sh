#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
OUT="/e/openclaw-work/comic/hiring-story/cover.png"
REF="/e/openclaw-work/comic/hiring-story/characters/characters.png"

PROMPT="Manga comic cover page, 3:4 portrait. Warm office interior, sunlight streaming through windows. 小雅HR female 28 ponytail black glasses white shirt holding coffee looking at camera with warm smile. A pile of resumes on her desk with post-it notes reading '已读不回'. Colorful 'HIRING' balloons hanging on the wall. Company cat sleeping on the sofa. Title text area at top for '一份让人心动的招聘广告'. Soft warm pastel tones, Japanese manga style, clean lineart, flat colors. Cover page composition with gentle light atmosphere."
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
