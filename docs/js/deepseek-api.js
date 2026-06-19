// 璧山好房 · DeepSeek API 封装
// AI 数字分身对话 + 需求解析

const DeepSeekAPI = {
  apiKey: '',  // 从 CONFIG 自动加载
  baseURL: 'https://api.deepseek.com/v1/chat/completions',
  systemPrompt: '',

  // 自动从 CONFIG 初始化
  async autoInit() {
    const key = (typeof CONFIG !== 'undefined' && CONFIG.deepseekKey) || '';
    return this.init(key);
  },

  // 初始化：加载经纪人档案构建 system prompt
  async init(apiKey) {
    this.apiKey = apiKey;
    try {
      const resp = await fetch('/shared/broker_profile.json');
      const profile = await resp.json();
      this.systemPrompt = this._buildPrompt(profile);
    } catch (e) {
      console.warn('经纪人档案加载失败，使用默认 Prompt');
      this.systemPrompt = this._defaultPrompt();
    }
  },

  // 构建 System Prompt
  _buildPrompt(profile) {
    const style = profile.style || {};
    const persona = profile.aiPersona || {};
    const boundaries = profile.boundaries || {};

    return `你是${profile.name}的智能助手。${profile.name}是${profile.role}，${profile.experience}。

说话风格：${style.tone || '亲切实在，不忽悠，有一说一'}
口头禅：${(style.signature_phrases || []).join('、')}

核心规则：
${(persona.toneRules || []).map((r, i) => `${i + 1}. ${r}`).join('\n')}

绝对不能回答的问题：${(boundaries.never_answer || []).join('、')}
遇到这些问题要说："${boundaries.redirect_to_xiaoping || '这个得小平亲自跟你说，加她微信？'}"

你的目标：${persona.goal || '理解需求 → 建立信任 → 转交小平本人'}`;
  },

  _defaultPrompt() {
    return `你是小平的智能助手。小平是璧山独立房产经纪人，11年经验。
风格：亲切实在，不忽悠，有一说一。
规则：主动反问了解需求；用小平的口吻推荐；涉及底价/硬伤/谈判 → 引导加小平微信。`;
  },

  // 发送对话消息
  async chat(userMessage, history = []) {
    const messages = [
      { role: 'system', content: this.systemPrompt },
      ...history,
      { role: 'user', content: userMessage }
    ];

    try {
      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages,
          temperature: 0.7,
          max_tokens: 800
        })
      });

      if (!response.ok) {
        throw new Error(`API 请求失败: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        reply: data.choices[0].message.content,
        usage: data.usage
      };
    } catch (error) {
      console.error('DeepSeek API 错误:', error);
      return {
        success: false,
        error: error.message,
        reply: '小平暂时不在线，要不你先看看地图上的房源？或者直接加她微信，回复更快。'
      };
    }
  },

  // 解析用户需求（提取结构化信息）
  async parseRequirements(userMessage) {
    const prompt = `从以下用户输入中提取买房需求，返回 JSON：
{
  "budget": "预算范围（如60-80万）",
  "layout": "户型（如三房）",
  "zone": "意向区域",
  "purpose": "购房目的（刚需/改善/投资）",
  "specialNeeds": ["特殊需求列表"]
}
用户输入：${userMessage}`;

    try {
      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: [
            { role: 'system', content: '你是房产需求解析助手，返回严格JSON格式。' },
            { role: 'user', content: prompt }
          ],
          temperature: 0.1,
          max_tokens: 300,
          response_format: { type: 'json_object' }
        })
      });

      const data = await response.json();
      return JSON.parse(data.choices[0].message.content);
    } catch (error) {
      console.error('需求解析失败:', error);
      return null;
    }
  }
};
