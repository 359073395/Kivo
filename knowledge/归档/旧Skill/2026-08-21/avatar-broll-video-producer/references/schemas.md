# Excel、目录与状态结构

## 任务目录

```text
<output_root>\
  <safe_sku>\
    <script_id>_<yyyymmdd>\
      00_task\
      01_product_white\
      02_presenter_gpt\
      03_audio_user\
      04_lipsync_heygen\
      05_broll\
        pain\
        product\
        usage\
        proof\
        lifestyle\
      06_excel\
      07_chatcut\
      08_output\
        draft\
        final\
      logs\
      ACTIVE_TASK.json
```

顶层按 SKU 隔离，同一 SKU 的不同文案按运行子目录隔离。全部路径保存为绝对路径；不得把任务文件写入 Skill 或同步盘目录。

## 文件职责与命名

- `01_product_white\<safe_sku>_product_white.*`：用户提供的产品白底图，是包装一致性的唯一主参考。
- `02_presenter_gpt\<safe_sku>_<script_id>_presenter_holding_product.png`：GPT 图像生成模型输出的手持产品人物图。
- `03_audio_user\<safe_sku>_<script_id>_voice_master.*`：用户提供并确认的唯一口播主轨。
- `04_lipsync_heygen\<safe_sku>_<script_id>_lipsync_master.mp4`：HeyGen 对口型底片。
- `05_broll\<function>\shotNN_<description>.*`：用户按搜索词收集的插入素材；保留原文件，不依赖文件夹顺序推断镜头。
- `06_excel\<safe_sku>_<script_id>_混剪执行表.xlsx`：该条视频的唯一执行表。
- `07_chatcut\`：ChatCut 项目 ID、导出记录或工程相关文件。
- `08_output\draft` 和 `08_output\final`：草稿与验收成片分离。

## Excel 工作簿

### 工作表一：视频任务

每条视频一行：

1. `task_id`
2. `店铺名`
3. `SKU`
4. `文案编号`
5. `印尼语完整文案`
6. `中文对照`
7. `目标时长秒`
8. `产品图`
9. `数字人图片`
10. `音频路径`
11. `音频哈希`
12. `音频时长秒`
13. `HeyGen底片提示词`
14. `HeyGen视频ID`
15. `数字人底片路径`
16. `ChatCut项目ID`
17. `最终视频路径`
18. `generation_policy_result`
19. `rights_confirmed`
20. `consent_confirmed`
21. `status`

### 工作表二：镜头与素材

每个时间段一行：

1. `task_id`
2. `镜头序号`
3. `开始时间秒`
4. `结束时间秒`
5. `对应印尼语口播`
6. `中文释义`
7. `镜头功能`
8. `画面类型`
9. `画面描述`
10. `英文搜索词1`
11. `英文搜索词2`
12. `英文搜索词3`
13. `印尼语搜索词1`
14. `印尼语搜索词2`
15. `中文搜索释义`
16. `禁用画面/负面词`
17. `图片生成提示词`
18. `本地图片路径`
19. `本地视频路径`
20. `素材来源/授权`
21. `字幕关键词`
22. `转场方式`
23. `素材状态`
24. `ChatCut素材名称`
25. `ChatCut轨道`
26. `素材入点秒`
27. `素材出点秒`
28. `保留HeyGen原音频`
29. `裁切方式`

### 工作表三：任务状态

至少记录产品白底图 QC、GPT 人物图 QC、用户音频哈希、HeyGen `video_id`、ChatCut 项目 ID、提交/完成/下载/混剪时间、尝试次数、校验结果、错误码、人工质检和披露状态。

### 工作表四：使用说明

说明搜索词使用方法、路径要求、状态含义、第一条测试门禁和人工复核要求。

## 状态机

```text
pending
→ preflight_ready
→ visual_plan_ready
→ presenter_image_ready
→ awaiting_user_audio
→ audio_ready
→ heygen_submitting
→ heygen_generating
→ avatar_downloaded
→ awaiting_user_broll
→ broll_ready
→ chatcut_submitting
→ chatcut_composing
→ validated
→ completed
```

特殊状态：`awaiting_asset_search`、`awaiting_batch_approval`、`auth_blocked`、`quota_blocked`、`chatcut_unavailable`、`unconfirmed`、`needs_user_review`、`skipped`。

JSON 更新先写 `.tmp`，刷新关闭后原子替换正式文件。
