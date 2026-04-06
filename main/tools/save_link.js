const { execSync } = require('child_process');

const cmd = `mcporter call tencent-docs create_smartcanvas_by_mdx title="📌 待阅读：对手哥文章" content_format="markdown" mdx="# 待阅读文章\n\n> 状态：待读取内容（微信公众号需授权登录）\n\n## 基本信息\n\n- **标题**：对手（来源：Seaborg的自留地）\n- **链接**：https://mp.weixin.qq.com/s/JFcHohMLurrCE8q92xEGnQ\n- **账号**：Seaborg的自留地\n- **添加时间**：2026-03-28\n\n## 摘要\n\n一篇关于「对手」的文章，具体内容待读取。\n\n## 问题记录\n\n微信公众号文章需要微信授权登录才能抓取全文。当前无法直接访问内容。\n\n## 后续行动\n\n- [ ] 方法1：在微信客户端打开文章，截图发给我分析\n- [ ] 方法2：复制全文内容粘贴过来\n- [ ] 方法3：等腾讯文档 Token 续期后重试\n- [ ] 方法4：安装 wechat-search skill 后尝试\n\n---\n*由 OpenClaw 自动创建于 2026-03-28*\n" parent_id="VnMoECPHHUGz`;

try {
  const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
  console.log(result);
} catch(e) {
  console.log(e.stdout);
  console.log(e.stderr);
}
