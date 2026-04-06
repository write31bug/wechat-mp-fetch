#!/bin/bash
SKILL="/e/openclaw-work/skills/baoyu-imagine/scripts/main.ts"

echo "Page 1 - 审判现场..."
npx -y bun "$SKILL" --prompt "Manga comic page 1, 3:4 portrait. 钱总 angry young female character standing center holding concert ticket in hand, looking at phone. WeChat group chat visible on phone screen showing question: 你们几个咋不来. Four male profiles shown as gray circles waiting. Bedroom background with MAYDAY poster on wall. Dramatic comedy manga style, exaggerated expression, Japanese manga clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p01.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 2 - 借口来了..."
npx -y bun "$SKILL" --prompt "Manga comic page 2, 3:4 portrait. Split panel showing four chat replies on phone screen. Fov replies: 我是Jay with Jay Chou music icon. 草莓园 replies: 我是棋士 with G.E.M. icon. 成 shows no reply gray. Rank shows no reply gray. Caption: 四个人的偶像应援色. Comedy manga style, phone chat UI style, expressive reactions, Japanese manga clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p02.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 3 - 钱总崩溃..."
npx -y bun "$SKILL" --prompt "Manga comic page 3, 3:4 portrait. 钱总 angry female character face extreme close-up shocked expression eyes wide, thought bubble showing confusion marks and question marks. Chat bubbles showing her message: 你们给我报偶像？？Jay是谁？棋士是下棋的吗？？ Japanese manga style dramatic comedy, exaggerated manga expressions, clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p03.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 4 - 四人装傻..."
npx -y bun "$SKILL" --prompt "Manga comic page 4, 3:4 portrait. Split panel showing four males pretending to be confused. Male 1 Fov: 阿？什么？我信号不好 你说什么？ Male 2 草莓园: 不好意思没看清 是演唱会吗？ Male 3 成: 嗯？ ？ 啊你说啥 Male 4 Rank: 在吗 刚才网卡了 不好意思哈. Each panel shows them acting innocent. Comedy manga style, Japanese manga clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p04.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 5 - 科普开始..."
npx -y bun "$SKILL" --prompt "Manga comic page 5, 3:4 portrait. Fov and 草莓园 excitedly sending music links and album covers in chat. Fov sending: 周杰伦！晴天！ 草莓园 sending: G.E.M.! 泡沫！ 钱总 watching chat fill with song links looking speechless and annoyed. Comedy manga style, chat flooded with music emojis and links, Japanese manga clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p05.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "Page 6 - 结尾..."
npx -y bun "$SKILL" --prompt "Manga comic ending page 6, 3:4 portrait. 钱总 sitting alone at MAYDAY concert venue, holding one荧光棒, four empty seats beside her with name tags: Fov 成 Rank 草莓园. Caption: 你们四个欠我四根荧光棒. Melancholic but funny ending, concert stage lights in background, warm sad atmosphere mixed with comedy. Japanese manga style clean lineart flat colors." --image "/e/openclaw-work/comic/accusation-story/p06.png" --provider dashscope --model qwen-image-2.0-pro --quality 2k

echo "All pages done!"
