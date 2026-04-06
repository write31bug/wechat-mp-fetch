#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Retry Page 2..."
npx -y bun "$SKILL" --prompt "Manga comic page 2 of 7, 3:4 portrait. Split panel showing diverse WeChat group members. Top panel: Chinese map of China showing group members scattered in cities Shenyang Guangzhou Wuhan Chengdu Beijing labeled with small icons. Bottom panel: phone screen showing WeChat group MAYDAY with 50 members chatting, showing friendly emoji reactions and concert ticket discussions. Caption: 群名就叫MAYDAY. Warm group chat feeling, colorful profile avatars, Japanese manga style, clean lineart flat colors." --image "/e/openclaw-work/comic/mayday-mayday/page-02.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 4..."
npx -y bun "$SKILL" --prompt "Manga comic page 4 of 7, 3:4 portrait. Concert venue exterior at night, crowd gathering. Five friends recognizing each other in the crowd - they found each other online months ago and now meet for real. They hold up matching荧光棒 in blue and pink. Caption: 一眼就能在人群里认出彼此. Warm concert atmosphere, colorful stage lights in background, excited happy expressions, Japanese manga style emotional storytelling, clean lineart flat colors warm tones." --image "/e/openclaw-work/comic/mayday-mayday/page-04.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 5..."
npx -y bun "$SKILL" --prompt "Manga comic page 5 of 7, 3:4 portrait. Late night street after concert, five friends sitting at a BBQ restaurant. Laughing and chatting over food and drinks. Beer bottles and skewers on the table. Warm yellow lantern lighting. Caption: 五个人默契地点了同意. Caption 2: 群名叫人生无限公司. Warm friendship atmosphere, emotional moment, Japanese manga style clean lineart flat colors." --image "/e/openclaw-work/comic/mayday-mayday/page-05.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Done batch 2!"
