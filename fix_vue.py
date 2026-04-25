with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# el-dialog 内容（应该在 </template> 之前）
dialog_content = '''
    <!-- Prompt详情对话框 -->
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
          <eludesc-item label="阶段">
            {{ selectedPrompt.stage }}
          </eludesc-item>
          <eludesc-item label="延迟">
            {{ selectedPrompt.latency_ms }} ms
          </eludesc-item>
          <eludesc-item label="时间戳">
            {{ selectedPrompt.timestamp }}
          </eludesc-item>
        </eludesc>
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
    </el-dialog>
'''

# 找到 </template> 的位置（最后一行应该是 </template>）
for i, line in enumerate(lines):
    if line.strip() == '</template>':
        print(f"Found </template> at line {i+1}")
        # 在这一行之前插入 el-dialog
        lines.insert(i, dialog_content)
        break

# 写回文件
with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Added el-dialog before closing template tag")
