#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Page 1..."
npx -y bun "$SKILL" --prompt "Manga comic page 1 of 7, 3:4 portrait. Late night bedroom scene, phone screen glowing on young person's face. Phone shows WeChat group chat: '2026五月天沈阳站' with comment '有没有沈阳的兄弟姐妹组队？' User profile pictures of different people from different cities. Excitement in the air. Caption: 三天后，你被拉进了一个群. Warm bedroom moonlight, Japanese manga style, emotional storytelling, clean lineart flat colors." --image "/e/openclaw-work/comic/mayday-mayday/page-01.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 2..."
npx -y bun "$SKILL" --prompt "Manga comic page 2 of 7, 3:4 portrait. Split panel showing diverse WeChat group members. Top panel: Chinese map of China showing group members from Shenyang Guangzhou Wuhan Chengdu Beijing labeled. Bottom panel: phone screen showing WeChat group MAYDAY with 50 members chatting about concert tickets. Caption: 群名就叫MAYDAY. Warm group chat feeling, multiple colorful profile avatars, Japanese manga style, clean lineart flat colors." --image "/e/openclaw-work/comic/mayday-mayday/page-02.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 3..."
npx -y bun "$SKILL" --prompt "Manga comic page 3 of 7, 3:4 portrait. Late night WeChat chat scene. Someone in group sends: 最近有点累 不知道为什么要活着. Silence for 5 minutes. Then messages appear one by one from different members: 我也曾经这样过 走出来之后更知道自己想要什么了. 不知道说什么 但我在. 你要是想聊聊 我睡不着 陪你说. Warm emotional scene, soft moonlight, chat bubbles glowing on dark phone screen. Caption: 那晚群里聊到凌晨三点. Japanese manga style, emotional storytelling, clean lineart flat colors." --image "/e/openclaw-work/comic/mayday-mayday/page-03.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Done batch 1!"
