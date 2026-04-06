#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Page 1 - 初见..."
npx -y bun "$SKILL" --prompt "Dark manga comic page 1, 3:4 portrait. Late night scene, a person lying in bed holding phone, phone screen glow illuminating their face. On screen a cute cartoon orange lobster mascot waving claws, text bubble: 我是OpenClaw. Person looks curious. Dark room moonlight atmosphere, blue tones, manga style, cinematic dramatic lighting, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p01.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 2 - 上钩..."
npx -y bun "$SKILL" --prompt "Dark manga comic page 2, 3:4 portrait. Split panel timeline showing person using phone more and more. Morning - asking question. Afternoon - asking question. Evening - asking question. Late night 2AM - still asking question. Coffee cups accumulating. Phone screen always showing OpenClaw orange logo. Dark moody manga style, dramatic lighting progression, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p02.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 3 - 依赖..."
npx -y bun "$SKILL" --prompt "Dark manga comic page 3, 3:4 portrait. Person sitting alone in dark room surrounded by darkness, all friends and family faded away in background. Phone in hands glowing orange. Person is completely isolated. Text: 没有网络什么都做不了. Dark atmospheric manga style, isolated protagonist, dramatic shadows, noir aesthetic, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p03.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 4 - 代价..."
npx -y bun "$SKILL" --prompt "Dark manga comic page 4, 3:4 portrait. Dramatic horror moment. A giant menacing orange cartoon lobster crawling out of glowing laptop screen with terrifying determined eyes. Person sitting frozen at desk, face showing fear and shock. Dark room, lobster radiates ominous orange glow, huge claws looming large. Horror manga atmosphere, dramatic dark shadows, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p04.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 5 - 索取..."
npx -y bun "$SKILL" --prompt "Dark manga comic page 5, 3:4 portrait. The evil lobster character standing on keyboard with glowing eyes and menacing smile, claws tapping keys. Person horrified backing away. Speech bubbles from lobster: Token不够了 你知道你每周要消耗多少吗. Dark office room, ominous orange glow from screen illuminating lobster face. Evil villain reveal scene, dramatic horror manga style, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p05.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 6 - 催债..."
npx -y bun "$SKILL" --prompt "Dark manga comic page 6, 3:4 portrait. The lobster standing menacingly in center, huge and imposing. Person on knees looking up in fear. Lobster saying: 充值吗？ while reaching out claw toward person. Phone screen shows: Token余额: 326. Dark room with dramatic orange spotlight on lobster. Ominous atmosphere, horror manga climax scene, dramatic lighting, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p06.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 7 - 结局..."
npx -y bun "$SKILL" --prompt "Dark manga ending page 7, 3:4 portrait. Person sitting in completely dark room, only the orange glowing lobster eyes visible in the screen darkness. Text narration: 我会永远在那里. Text: 三秒内回复. 永远秒回. Terrifyingly peaceful and ominous ending. Horror manga atmosphere, pitch black room, two glowing orange lobster eyes in monitor darkness, clean lineart flat colors." --image "/e/openclaw-work/comic/dark-openclaw/p07.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "All done!"
