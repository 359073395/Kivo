# HeyGen 数字人底片与音频主轨

## 与纯口播模式的区别

本模式的 HeyGen 提示词只描述数字人的稳定表演和构图。输入固定为 GPT 生成且已验收的手持产品人物图，以及用户提供并锁定的最终语音。痛点场景、使用步骤、产品 B-roll、文字卡和转场全部写入镜头表并交给 ChatCut 完成。

不要在 HeyGen 提示词中要求：

- 自动插入产品使用画面或场景 B-roll。
- 改变背景、服装、产品、包装或镜头位置。
- 大幅挥手、转身、遮嘴或复杂道具操作。
- 自动生成字幕、价格、评价、认证或促销卡。

## 默认提示词骨架

```text
Create a stable 9:16 lip-sync presenter base video from the supplied image and supplied final audio. Preserve the exact presenter, face, clothing, background, lighting, camera angle, product shape, packaging, label, logo, cap/nozzle and product position throughout. Keep the product front label facing the camera and keep the mouth unobstructed. Use natural lip sync, steady eye contact, tiny nods, subtle facial movement and minimal upper-body motion. Do not rotate, bend, duplicate, resize or relabel the product. Do not add B-roll, scene changes, extra objects, on-screen text, captions, prices, claims, music or transitions. Preserve the supplied audio without rewriting or replacing it. Preserve all platform AI labels and watermarks.
```

根据文案段落只补充 2–4 个面部或头部微动作，例如开场看镜头、卖点处轻点头、顾虑处理处轻微摇头和 CTA 时轻微微笑。手持产品时不要求抬举、转瓶、指点标签或复杂手势。不要把 B-roll 描述塞进 HeyGen 提示词。

## 音频主轨

- 只接受用户提供的最终语音；缺少音频时停在 `awaiting_user_audio`。
- 验证音频存在、非零、可解码、无明显削波、无人声以外的强背景声，并记录语言、来源、授权、时长和 SHA-256。
- 优先接受 WAV、MP3、M4A 或 HeyGen 当前接口明确支持的音频格式；禁止把带 BGM 的完整成片当作口播主轨。
- 只上传这一份锁定音频驱动 image lip-sync；不得让 HeyGen 重新生成、改写或替换声音。
- 用户更换音频后必须生成新哈希和新版本，不得覆盖已提交的远端任务。
- 文案或语音变化后建立新版本，不覆盖已经提交的远端任务。

## 提交与恢复

- 固定使用 HeyGen MCP OAuth，不读取或请求 API key。
- 点击/调用创建前写提交意图；保存请求 ID 或 `video_id`。
- 当前条完成、明确失败或人工暂停前不提交下一条。
- 状态不明确时先查 manifest、远端列表和本地文件，不重复创建。
- 身份验证、API credits、套餐或接口错误时按原错误暂停；不得切换到另一条 HeyGen 创建路线规避限制。
