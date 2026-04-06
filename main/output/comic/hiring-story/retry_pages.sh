#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Retry page 06..."
npx -y bun "$SKILL" --prompt "Manga comic page 6 of 10, 3:4 portrait. Four panel split showing four different warm interview moments. Panel 1: 阿明 presenting project to smiling interviewer who says 这个创意我很喜欢. Panel 2: 王姐 showing architecture portfolio to interviewer discussing career change. Panel 3: 小林 sitting quietly as interviewer hands him pen saying 写代码不用电脑用手就好. Panel 4: CEO老张 playing 小北 game demo laughing saying 你的游戏我打到第二关就上瘾了. Warm cozy interview room backgrounds. Japanese manga style warm tone." --image "/e/openclaw-work/comic/hiring-story/page-06.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Retry page 07..."
npx -y bun "$SKILL" --prompt "Manga comic page 7 of 10, 3:4 portrait. Four close-up reaction panels showing each character receiving job offer. Panel 1: 阿明 jumping with joy receiving email notification. Panel 2: 王姐 putting down pen quietly, eyes slightly red with happy tears. Panel 3: 小林 smiling slightly at screen, coworkers in background noticing being surprised. Panel 4: 小北 taking selfie making peace sign, sending to mom with text 妈我找到组织了. Bright warm sunshine from window. Japanese manga style expressive emotions." --image "/e/openclaw-work/comic/hiring-story/page-07.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Retry page 08..."
npx -y bun "$SKILL" --prompt "Manga comic page 8 of 10, 3:4 portrait. Company break room on first day. Homemade celebration cake on table with each new hire name decorated. 小雅 HR distributing welcome badges. Four new hires standing together looking happy. Badge tags: 小林擅长深夜debug, 王姐会做一手好饭, 小北会弹吉他, 阿明擅长把deadline变成玩笑. Company cat on sofa. Warm sunshine, cozy office. Japanese manga style warm tone." --image "/e/openclaw-work/comic/hiring-story/page-08.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Retry page 09..."
npx -y bun "$SKILL" --prompt "Manga comic page 9 of 10, 3:4 portrait. One month later workplace scene. Warm busy office. 阿明 and 王姐 discussing at whiteboard. 小林 coding with headphones in quiet corner, coworker placed ergonomic keyboard beside him. 小北 and CEO老张 reviewing product demo laughing together. Wall covered with team photos and joy notes. Golden hour sunlight. Japanese manga style warm tone group harmony." --image "/e/openclaw-work/comic/hiring-story/page-09.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Retry page 10..."
npx -y bun "$SKILL" --prompt "Manga comic ending page 10 of 10, 3:4 portrait. Evening scene, company entrance. New job ad poster reads: 这一次 我们在等你带来你的故事. Poster has four illustrated happy faces matching four new hires. 小雅 walking past smiling. Golden sunset light. Bottom text: 星光科技 招聘持续进行中. Warm nostalgic hopeful ending. Japanese manga style clean lineart." --image "/e/openclaw-work/comic/hiring-story/page-10.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "All retries done!"
