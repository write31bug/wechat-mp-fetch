#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Retry page 6..."
npx -y bun "$SKILL" --prompt "Manga comic ending page 6 of 6, 3:4 portrait. 钱总 sitting alone at MAYDAY concert venue, holding one荧光棒, four empty seats beside her with small name tags: Fov 成 Rank 草莓园. Concert stage with colorful lights in background, a single spotlight on her. Melancholic but funny ending. Caption: 你们四个欠我四根荧光棒. Warm concert atmosphere, comedy tragedy mix, Japanese manga style clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p06.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Done p6"
