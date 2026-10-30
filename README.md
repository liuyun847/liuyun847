# liuyun847

Repository index — plugins and tools.

这里是 [liuyun847](https://github.com/liuyun847) 名下公开仓库的索引，按用途分组，方便查找。

<!-- AUTO:START -->
最后更新：2026-10-30

## DSH 插件

DeepSeek Harness(DSH)的宿主插件与 Web 客户端插件。

| 仓库 | 说明 |
|---|---|
| [dsh-agent-preset-coordinator](https://github.com/liuyun847/dsh-agent-preset-coordinator) | DSH 预设组合包:协调者预设 + project-coordination 技能与校验工具 (DeepSeek Harness) |
| [dsh-client-ui-peak-valley](https://github.com/liuyun847/dsh-client-ui-peak-valley) | DSH 客户端插件:模型选择按钮左侧显示 DeepSeek API 峰/谷价状态(绿=谷,橙=峰) |
| [dsh-client-ui-session-rail](https://github.com/liuyun847/dsh-client-ui-session-rail) | DSH 客户端插件:侧边栏收起时在左侧空白区竖排显示活跃会话横条 (DeepSeek Harness) |
| [dsh-client-ui-turn-chime](https://github.com/liuyun847/dsh-client-ui-turn-chime) | DSH 客户端插件:AI 回复完成时播放双音提示音 (DeepSeek Harness) |
| [dsh-host-goal-subagent-gate](https://github.com/liuyun847/dsh-host-goal-subagent-gate) | DSH 宿主插件:有在飞子代理时压住 goal 自动续轮,避免空转烧额度 (DeepSeek Harness) |
| [dsh-host-ptc-lazy](https://github.com/liuyun847/dsh-host-ptc-lazy) | DSH 宿主插件:把 ptc 会话系统提示词里的全量工具签名换成按组懒加载(签名注入对话尾部,不破缓存) |
| [dsh-host-restart](https://github.com/liuyun847/dsh-host-restart) | DSH 宿主插件:给模型一个 restart_dsh 工具,重启 dsh 后自动恢复原会话续跑 (DeepSeek Harness) |
| [dsh-host-sl](https://github.com/liuyun847/dsh-host-sl) | DSH 宿主插件:活跃工作表+崩溃重启后冷恢复唤醒未完成会话并附断点,子代理接续结果回报父会话 (DeepSeek Harness) |
| [dsh-host-task-board](https://github.com/liuyun847/dsh-host-task-board) | DSH 宿主插件:协调者预设专用的共享任务板工具 task_board,落宿主领域存储跨重启存活 (DeepSeek Harness) |
| [dsh-host-tool-layering](https://github.com/liuyun847/dsh-host-tool-layering) | DSH 宿主插件:按前缀把整组工具从模型可见工具表摘掉,改由技能当说明书,省上下文 (DeepSeek Harness) |
| [dsh-llm-auto](https://github.com/liuyun847/dsh-llm-auto) | DSH 宿主插件:注册 auto 模型,按有序回退链在多条 provider+model 间静默切换 (DeepSeek Harness) |
| [dsh-skill-toggle](https://github.com/liuyun847/dsh-skill-toggle) | DSH 插件:把名单里的技能标成模型不可调用(模型目录与 skill 工具看不到),用户 /名字 仍可用,带设置页开关 (DeepSeek Harness) |

## 工具与项目

| 仓库 | 说明 |
|---|---|
| [adaptive-reader](https://github.com/liuyun847/adaptive-reader) | 阅读文本自适应重写工具：段锚点→概念清单→逐段改写→事实锚校验→阅读器（Python/uv） |
| [crafting-calculator](https://github.com/liuyun847/crafting-calculator) | 自动化建造游戏通用合成计算器，支持多游戏配方、生产链计算和路径对比 |
| [divination](https://github.com/liuyun847/divination) | 三枚铜钱法起卦 CLI 工具，结合 AI 进行解卦 |
| [lambda-calculus](https://github.com/liuyun847/lambda-calculus) | 零依赖的 Python λ 演算迷你语言：解析变量、抽象与应用，支持最左最外 β/η 归约，并附 Python 原生 lambda 对照演示。 |
| [text2video](https://github.com/liuyun847/text2video) | 文案转视频：edge-tts 配音 + 滚动字幕 + ffmpeg 合成 |
| [vision-cli](https://github.com/liuyun847/vision-cli) | 图片分析命令行工具，可以作为 Skill 使用，使纯文本模型能够理解图片 |
| [vlm-gui-tools](https://github.com/liuyun847/vlm-gui-tools) | 为视觉语言模型(VLM)提供屏幕截图网格标注和鼠标点击控制的SKILL |

## 学习与示例

| 仓库 | 说明 |
|---|---|
| [demo](https://github.com/liuyun847/demo) | Godot 游戏开发示例项目 |
| [learn](https://github.com/liuyun847/learn) | Python 学习项目 |

## Fork

| 仓库 | 说明 |
|---|---|
| [ok-wuthering-waves](https://github.com/liuyun847/ok-wuthering-waves) | 鸣潮 后台自动战斗 自动刷声骸 一键日常  Automation for Wuthering Waves；上游 [ok-oldking/ok-wuthering-waves](https://github.com/ok-oldking/ok-wuthering-waves) 的 fork |

<!-- AUTO:END -->

---

<sub>本页由 GitHub Actions 自动更新，分组规则见 [`repos.toml`](repos.toml)。</sub>
