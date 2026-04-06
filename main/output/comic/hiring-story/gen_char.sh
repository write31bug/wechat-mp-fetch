#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"
OUT="/e/openclaw-work/comic/hiring-story/characters/characters.png"
PROMPT="Character reference sheet manga style five characters white background labeled with Chinese names. 小雅HR女28岁圆脸马尾黑框眼镜白衬衫半裙温暖笑容咖啡杯. 阿明求职者男23岁眼镜微胖格子衫双肩包学生气. 王姐转行者女35岁短发职业装沉稳. 小林程序员男26岁瘦卫衣耳机挂脖腼腆微笑. 老张CEO男40岁T恤牛仔裤亲切幽默. 日漫风格扁平色彩暖色调白底站立正面高质量插画"
npx -y bun "$SKILL" --prompt "$PROMPT" --image "$OUT" --provider dashscope --model qwen-image-2.0-pro --quality 2k
