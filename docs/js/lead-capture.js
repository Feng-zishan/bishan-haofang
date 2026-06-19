// 璧山好房 · 留资系统
// 需求卡片 + EmailJS 邮件通知

const LeadCapture = {
  emailJS: {
    serviceID: '',    // EmailJS Service ID
    templateID: '',   // EmailJS Template ID
    publicKey: ''     // EmailJS Public Key
  },

  // 初始化 EmailJS
  init(config = {}) {
    this.emailJS = { ...this.emailJS, ...config };
  },

  // 收集浏览行为（页面停留、浏览楼盘）
  trackView(loupanId, loupanName) {
    const views = JSON.parse(sessionStorage.getItem('viewedLoupan') || '[]');
    if (!views.find(v => v.id === loupanId)) {
      views.push({ id: loupanId, name: loupanName, time: Date.now() });
      sessionStorage.setItem('viewedLoupan', JSON.stringify(views));
    }
  },

  // 获取浏览记录
  getViews() {
    return JSON.parse(sessionStorage.getItem('viewedLoupan') || '[]');
  },

  // 构建需求画像（AI对话 + 浏览行为）
  buildProfile(aiRequirements, viewedLoupan) {
    return {
      requirements: aiRequirements || {},
      viewed: viewedLoupan || this.getViews(),
      timestamp: new Date().toISOString()
    };
  },

  // 提交留资（发送邮件给小平）
  async submit(profile, phone = '') {
    const payload = {
      type: 'lead',
      profile,
      phone,
      source: document.referrer || '直接访问',
      page: window.location.href
    };

    // 如果有 EmailJS 配置，发送邮件
    if (this.emailJS.publicKey) {
      try {
        // EmailJS 发送
        const resp = await emailjs.send(
          this.emailJS.serviceID,
          this.emailJS.templateID,
          {
            to_email: 'xiaoping@example.com',  // TODO: 替换为小平实际邮箱
            subject: `新线索：${phone || '未留电话'} - ${profile.requirements.purpose || '未知需求'}`,
            message: JSON.stringify(payload, null, 2),
            phone: phone || '未留',
            requirements: profile.requirements.purpose || '未识别',
            viewed: profile.viewed.map(v => v.name).join('、') || '无'
          },
          this.emailJS.publicKey
        );
        return { success: true, method: 'email' };
      } catch (error) {
        console.error('留资提交失败:', error);
        // 降级：保存到本地存储
        this._saveLocal(payload);
        return { success: false, error: error.message, method: 'local' };
      }
    }

    // 无 EmailJS 配置，存本地
    this._saveLocal(payload);
    return { success: true, method: 'local' };
  },

  // 本地存储兜底
  _saveLocal(payload) {
    const leads = JSON.parse(localStorage.getItem('pendingLeads') || '[]');
    leads.push(payload);
    localStorage.setItem('pendingLeads', JSON.stringify(leads));
  },

  // 获取本地留资
  getLocalLeads() {
    return JSON.parse(localStorage.getItem('pendingLeads') || '[]');
  }
};
