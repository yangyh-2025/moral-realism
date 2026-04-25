# 重新读取文件并正确地添加 el-dialog
with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到所有 <!-- Prompt详情对话框--> 和 </el-dialog> 位置
import re

# 查找所有 Prompt详情对话框 标记
matches = list(re.finditer(r'<!-- Prompt详情对话框-->.*?</el-dialog>', content, re.DOTALL))

if matches:
    print(f'Found {len(matches)} el-dialog blocks')
    for i, match in enumerate(matches):
        print(f'  Match {i+1}: position {match.start()}-{match.end()}')
        # 检查是否有乱码的字符
        dialog_text = match.group()
        if 'LLM' in dialog_text:
            # 检查是否有乱码
            try:
                # 简单替换整个 el-dialog 部分
                correct_dialog = '''    <!-- Prompt详情对话框 -->
    <el-dialog
      v-model="showPromptDetail"
      title="LLM Prompt详情"
      width="80%"
    >
      <div v-if="selectedPrompt">
        <el-tabs>
          <el-tab-pane label="System Prompt">
            <el-input
              type="textarea"
              :rows="20"
              :model-value="selectedPrompt.full_system_prompt"
              readonly
            />
          </el-tab-pane>
          <el-tab-pane label="User Prompt">
            <el-input
              type="textarea"
              :rows="20"
              :model-value="selectedPrompt.full_prompt"
              readonly
            />
          </el-tab-pane>
          <el-tab-pane label="LLM响应">
            <el-input
              type="textarea"
              :rows="10"
              :model-value="JSON.stringify(selectedPrompt.full_response, null, 2)"
              readonly
            />
          </el-tab-pane>
        </el-tabs>
        <el-descriptions style="margin-top: 10px;" :column="2" border size="small">
          <el-descriptions-item label="智能体">
            {{ selectedPrompt.agent_name }} (ID: {{ selectedPrompt.agent_id }})
          </el-descriptions-item>
          <el-descriptions-item label="阶段">
            {{ selectedPrompt.stage }}
          </el-descriptions-item>
          <el-descriptions-item label="延迟">
            {{ selectedPrompt.latency_ms }} ms
          </el-descriptions-item>
          <el-descriptions-item label="时间戳">
            {{ selectedPrompt.timestamp }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else-if="llmPrompts.length > 0">
        <el-collapse>
          <el-collapse-item
            v-for="(prompt, index) in llmPrompts"
            :key="index"
            :title="`${prompt.agent_name} (${prompt.stage})`"
          >
            <el-tabs>
              <el-tab-pane label="System Prompt">
                <el-input
                  type="textarea"
                  :rows="15"
                  :model-value="prompt.full_system_prompt"
                  readonly
                />
              </el-tab-pane>
              <el-tab-pane label="User Prompt">
                <el-input
                  type="textarea"
                  :rows="15"
                  :model-value="prompt.full_prompt"
                  readonly
                />
              </el-tab-pane>
              <el-tab-pane label="LLM响应">
                <el-input
                  type="textarea"
                  :rows="10"
                  :model-value="JSON.stringify(prompt.full_response, null, 2)"
                  readonly
                />
              </el-tab-pane>
            </el-tabs>
          </el-collapse-item>
        </el-collapse>
      </div>
      <div v-else>
        <el-empty description="暂无LLM Prompt数据" />
      </div>
    </el-dialog>'''

                # 替换
                content = content[:match.start()] + correct_dialog + content[match.end():]

                # 写回文件
                with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'w', encoding='utf-8') as f:
                    f.write(content)

                print('Fixed: Replaced corrupted el-dialog with correct version')
                break
            except Exception as e:
                print(f'Encoding error: {e}')
else:
    print('No el-dialog found')
