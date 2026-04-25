# 重新读取文件并构建正确的文件
with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到第一个 </template> 之前的内容（这是主要部分）
template_sections = []
last_end = 0
for match in content.finditer('</template>'):
    start = last_end
    end = match.start() + len('</template>')
    template_sections.append(content[start:end])
    last_end = end

print(f'Found {len(template_sections)} </template> sections')

# 第一段是template部分，应该包含el-dialog但不在 </template> 外
# 找到错误的 el-dialog（在 template 部分之前）
if '<!-- Prompt详情对话框-->' in template_sections[0]:
    # 这是一个错误，el-dialog 应该在最后一个 </template> 之前
    print('Found el-dialog in wrong position (before first </template>)')

    # 找到这个错误位置的 el-dialog 部分并删除它
    wrong_start = template_sections[0].find('<!-- Prompt详情对话框-->')
    if wrong_start != -1:
        # 找到对应的 </el-dialog>
        wrong_end = template_sections[0].find('</el-dialog>', wrong_start)
        if wrong_end != -1:
            wrong_end += len('</el-dialog>')

            # 删除这个错误的部分
            clean_first_section = template_sections[0][:wrong_start] + template_sections[0][wrong_end:]

            # 找到最后一个 </template> 的位置
            last_template_end = content.rfind('</template>')
            if last_template_end != -1:
                # 在最后一个 </template> 之前插入 el-dialog
                insert_pos = last_template_end

                el_dialog_content = '''
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
    </el-dialog>
'''

                # 重新构建文件
                # 找到最后一部分（script、style等）
                final_part = content[last_template_end:]

                # 第一部分使用清理后的模板部分
                new_first_part = clean_first_section
                # 其他部分保持不变
                other_parts = template_sections[1:]

                # 重新组装
                new_content = new_first_part + ''.join(other_parts)
                # 在最后一个 </template> 之前插入 el-dialog
                new_content = new_content[:insert_pos] + el_dialog_content + new_content[insert_pos:]

                # 写回文件
                with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print('Fixed: Moved el-dialog to correct position')
else:
    print('Could not find </template> sections')
