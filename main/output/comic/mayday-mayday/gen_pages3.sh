#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Page 6..."
npx -y bun "$SKILL" --prompt "Manga comic page 6 of 7, 3:4 portrait. Split panel showing warm daily moments in WeChat group. Panel 1: late night chat - someone says 我不行了 another replies 出来请你喝奶茶 with a red envelope emoji. Panel 2: someone shares news of quitting job, group analyzes together until dawn. Panel 3: someone posts new relationship photo, chat fills with celebration emojis. Caption: 人生无限公司 日常. Warm cozy phone screen glow, Japanese manga style emotional storytelling, clean lineart flat colors." --image "/e/openclaw-work/comic/mayday-mayday/page-06.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 7..."
npx -y bun "$SKILL" --prompt "Manga comic ending page 7 of 7, 3:4 portrait. A screenshot of a WeChat group chat showing someone posted an old concert photo with MAYDAY band. Caption in chat: 如果你们不曾疯过 我们怎么敢老去. Then a chain of replies: 三十岁演唱会见. 三十五岁演唱会见. 四十岁也要去. 就算坐轮椅 也要举着荧光棒去. A warm glowing phone screen in darkness. Caption: 故事还在继续. Emotional hopeful ending, Japanese manga style clean lineart flat colors warm tones." --image "/e/openclaw-work/comic/mayday-mayday/page-07.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Done all pages!"
