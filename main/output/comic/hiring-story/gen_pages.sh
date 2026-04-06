#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Generating page 02..."
npx -y bun "$SKILL" --prompt "Manga comic page 2 of 10, 3:4 portrait. Meeting room scene, warm lighting. 老张 male CEO 40 casual t-shirt jeans relaxed pose feet on desk laughing. 小雅 HR female 28 ponytail black glasses listening carefully. Speech bubble text: JD谁都会写 但一封让人想加入的信 不是谁都能写的. Japanese manga style warm tone clean lineart flat colors." --image "/e/openclaw-work/comic/hiring-story/page-02.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 03..."
npx -y bun "$SKILL" --prompt "Manga comic page 3 of 10, 3:4 portrait. Late night office scene, warm desk lamp light. 小雅 HR female 28 at desk drawing a hand-drawn job ad poster with colorful markers. Coffee cup and sticky notes scattered. The poster on wall shows: cat illustration, team photo sketch, text: 我们不只是找员工 我们找队友. Warm cozy atmosphere, Japanese manga style clean lineart flat colors." --image "/e/openclaw-work/comic/hiring-story/page-03.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 04..."
npx -y bun "$SKILL" --prompt "Manga comic page 4 of 10, 3:4 portrait. Four split panels showing four characters seeing the job ad on their phones. Panel 1: 阿明 male 23 glasses plaid shirt backpack in dorm room eyes lighting up. Panel 2: 王姐 female 35 short hair professional attire in cafe pausing coffee stirring. Panel 3: 小林 male 26 hoodie headphones programmer in dark room stopping coding to read phone. Panel 4: 小北 gender-neutral artistic style person in creative studio forwarding to friend saying 这家公司有点意思. Center ad slogan: 你将和一群相信热爱比加班更重要的人工作. Warm pastel manga style." --image "/e/openclaw-work/comic/hiring-story/page-04.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 05..."
npx -y bun "$SKILL" --prompt "Manga comic page 5 of 10, 3:4 portrait. Company entrance lobby. Four job seekers arriving together shyly. 小雅 HR female 28 ponytail welcoming them at door holding handmade welcome cards. Company cat sitting nearby. Four characters: 阿明 with backpack looking nervous, 王姐 confident posture, 小林 with headphones around neck nodding, 小北 taking photo of company sign. Warm sunshine through lobby windows. Japanese manga style clean lineart flat colors." --image "/e/openclaw-work/comic/hiring-story/page-05.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 06..."
npx -y bun "$SKILL" --prompt "Manga comic page 6 of 10, 3:4 portrait. Four panel split showing four different warm interview moments. Panel 1: 阿明 presenting project to smiling interviewer who says 这个创意我很喜欢. Panel 2: 王姐 showing architecture portfolio to interviewer discussing career change. Panel 3: 小林 sitting quietly as interviewer hands him pen saying 写代码不用电脑用手就好. Panel 4: CEO老张 playing 小北 game demo laughing saying 你的游戏我打到第二关就上瘾了. Warm cozy interview room backgrounds. Japanese manga style warm tone." --image "/e/openclaw-work/comic/hiring-story/page-06.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 07..."
npx -y bun "$SKILL" --prompt "Manga comic page 7 of 10, 3:4 portrait. Four close-up reaction panels showing each character receiving job offer. Panel 1: 阿明 jumping with joy receiving email notification. Panel 2: 王姐 putting down pen quietly, eyes slightly red with happy tears. Panel 3: 小林 smiling slightly at screen, coworkers in background noticing and being surprised. Panel 4: 小北 taking selfie making peace sign, sending to mom with text 妈我找到组织了. Bright warm sunshine from window. Japanese manga style expressive emotions clean lineart." --image "/e/openclaw-work/comic/hiring-story/page-07.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 08..."
npx -y bun "$SKILL" --prompt "Manga comic page 8 of 10, 3:4 portrait. Company break room on first day. Homemade celebration cake on table with each new hire name decorated. 小雅 HR distributing welcome badges. Four new hires standing together looking happy and relieved. Badge details show personality tags: 小林: 擅长深夜debug, 王姐: 会做一手好饭, 小北: 会弹吉他, 阿明: 擅长把deadline变成玩笑. Company cat on sofa watching. Warm sunshine, cozy office plants in background. Japanese manga style warm tone clean lineart flat colors." --image "/e/openclaw-work/comic/hiring-story/page-08.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 09..."
npx -y bun "$SKILL" --prompt "Manga comic page 9 of 10, 3:4 portrait. One month later workplace scene. Warm busy office atmosphere. 阿明 and 王姐 discussing enthusiastically at whiteboard. 小林 coding with headphones in his own quiet corner, coworker placed ergonomic keyboard beside him. 小北 and CEO老张 reviewing product demo together laughing. Background wall covered with team photos, sticky notes, and a joy wall with handwritten notes. Warm golden hour sunlight through windows. Japanese manga style warm tone, group harmony feeling." --image "/e/openclaw-work/comic/hiring-story/page-09.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Generating page 10..."
npx -y bun "$SKILL" --prompt "Manga comic ending page 10 of 10, 3:4 portrait. Evening scene, company entrance. New job ad poster on wall reads: 这一次 我们在等你带来你的故事. Poster has four illustrated happy faces matching the four new hires from the story. 小雅 walking past looking at the poster with smile. Golden sunset light. Tagline small text at bottom: 星光科技 招聘持续进行中. Warm nostalgic atmosphere, Japanese manga style, hopeful ending feeling, clean lineart flat colors." --image "/e/openclaw-work/comic/hiring-story/page-10.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "All pages done!"
