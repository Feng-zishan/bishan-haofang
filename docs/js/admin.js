// 璧山好房 · 后台管理逻辑
// 数据看板、楼盘/文章编辑、留资管理

const Admin = {
  // 密码验证（简单保护）
  checkPassword(input) {
    const stored = localStorage.getItem('admin_password');
    if (!stored) {
      // 首次设置密码
      localStorage.setItem('admin_password', input);
      return true;
    }
    return input === stored;
  },

  // 加载数据看板
  async loadDashboard() {
    try {
      const [loupanResp, leads] = await Promise.all([
        fetch('/shared/loupan_list.json'),
        Promise.resolve(LeadCapture.getLocalLeads())
      ]);
      const loupanData = await loupanResp.json();

      return {
        totalLoupan: loupanData.totalCount || loupanData.loupanList.length,
        totalLeads: leads.length,
        newLeadsToday: leads.filter(l => {
          const t = new Date(l.profile?.timestamp);
          const today = new Date();
          return t.toDateString() === today.toDateString();
        }).length,
        avgPrice: Math.round(
          loupanData.loupanList.reduce((s, l) => s + l.avgPrice, 0) / loupanData.loupanList.length
        )
      };
    } catch (e) {
      console.error('看板数据加载失败:', e);
      return null;
    }
  },

  // 更新楼盘数据
  async updateLoupan(loupanId, updates) {
    // 注意：纯前端无法直接修改服务器文件
    // 实际部署时走 GitHub API 或本地 git 操作
    console.log('更新楼盘:', loupanId, updates);
    // TODO: 实现 GitHub API 更新 shared/loupan_list.json
  },

  // 导出留资
  exportLeads() {
    const leads = LeadCapture.getLocalLeads();
    const csv = [
      ['时间', '电话', '需求类型', '浏览楼盘'],
      ...leads.map(l => [
        l.profile?.timestamp || '',
        l.phone || '',
        l.profile?.requirements?.purpose || '',
        (l.profile?.viewed || []).map(v => v.name).join(';')
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `留资导出_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }
};
