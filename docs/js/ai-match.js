// 璧山好房 · AI 需求匹配
// 解析用户需求 → 匹配楼盘数据 → 返回推荐结果

const AIMatcher = {
  loupanData: [],

  // 加载楼盘数据
  async loadData() {
    try {
      const resp = await fetch('/shared/loupan_list.json');
      const data = await resp.json();
      this.loupanData = data.loupanList || [];
      return this.loupanData.length;
    } catch (e) {
      console.error('楼盘数据加载失败:', e);
      return 0;
    }
  },

  // 本地匹配（基于标签和价格）
  matchLocal(requirements) {
    let results = [...this.loupanData];

    // 按区域筛选
    if (requirements.zone) {
      const zoneFilter = results.filter(l =>
        l.zone.includes(requirements.zone) || l.zoneId === requirements.zone
      );
      if (zoneFilter.length > 0) results = zoneFilter;
    }

    // 按户型筛选
    if (requirements.layout) {
      const layoutFilter = results.filter(l =>
        l.layout.some(ly => ly.includes(requirements.layout.replace(/[0-9]/g, '')) || requirements.layout.includes(ly.replace(/[两三四五]/, '')))
      );
      if (layoutFilter.length > 0) results = layoutFilter;
    }

    // 按预算筛选
    if (requirements.budget) {
      const budgetMatch = requirements.budget.match(/\d+/g);
      if (budgetMatch && budgetMatch.length >= 1) {
        const maxBudget = parseInt(budgetMatch[budgetMatch.length - 1]);
        if (maxBudget) {
          results = results.filter(l => {
            const totalPrice = l.avgPrice * (l.areaRange[0] + l.areaRange[1]) / 2 / 10000;
            return totalPrice <= maxBudget * 1.2; // 留20%上浮空间
          });
        }
      }
    }

    // 按类型筛选
    if (requirements.purpose) {
      if (requirements.purpose.includes('刚需')) {
        results.sort((a, b) => a.avgPrice - b.avgPrice);
      } else if (requirements.purpose.includes('改善')) {
        results.sort((a, b) => b.avgPrice - a.avgPrice);
      }
    }

    // 按评分排序
    results.sort((a, b) => b.rating - a.rating);

    return results.slice(0, 5); // 最多返回5套
  },

  // 生成推荐语
  generateSummary(results, requirements) {
    if (results.length === 0) {
      return '璧山暂时没有完全匹配的房源，要不你跟小平说说你的具体情况？她对每一片都熟，也许有没上架的合适房源。';
    }

    const zone = requirements.zone || '璧山';
    const count = results.length;
    const topPick = results[0];

    return `小平帮你在${zone}筛了${count}套，${topPick.name}性价比不错——${topPick.brokerComment.slice(0, 40)}... 看看合不合适？`;
  }
};
