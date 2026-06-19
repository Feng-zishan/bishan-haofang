// 璧山好房 · 应用主逻辑
// 路由、导航、页面切换、通用工具

const APP = {
  version: '1.0.0',
  currentScreen: null,
  navStack: [],
  isGoingBack: false,

  // 初始化
  init() {
    this.detectDevice();
    this.bindNavigation();
    this.initServiceWorker();
    console.log(`🏠 璧山好房 v${this.version} 已就绪`);
  },

  // 设备检测
  detectDevice() {
    const isMobile = window.innerWidth < 768;
    document.documentElement.dataset.device = isMobile ? 'mobile' : 'desktop';
    return isMobile;
  },

  // 页面导航
  goTo(screenId) {
    if (!this.isGoingBack && this.currentScreen && this.currentScreen !== screenId) {
      this.navStack.push(this.currentScreen);
    }
    this.isGoingBack = false;

    // 隐藏所有页面
    document.querySelectorAll('.screen').forEach(s => {
      s.style.display = 'none';
    });

    // 显示目标页面
    const target = document.getElementById(screenId);
    if (target) {
      target.style.display = 'block';
      this.currentScreen = screenId;
      window.scrollTo(0, 0);
    }
  },

  // 返回上一页
  goBack() {
    // 先检查是否有打开的面板
    const panels = document.querySelectorAll('.overlay-mask');
    if (panels.length > 0) {
      panels[panels.length - 1].remove();
      return;
    }
    if (this.navStack.length === 0) return;
    this.isGoingBack = true;
    this.goTo(this.navStack.pop());
  },

  // 导航绑定
  bindNavigation() {
    document.querySelectorAll('[data-nav]').forEach(el => {
      el.addEventListener('click', () => {
        const target = el.dataset.nav;
        if (target) this.goTo(target);
      });
    });
  },

  // Service Worker 注册
  initServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/web/sw.js').catch(() => {
        // 离线环境下注册失败是正常的
      });
    }
  },

  // 工具：格式化价格
  formatPrice(price) {
    if (price >= 10000) {
      return (price / 10000).toFixed(1) + '万';
    }
    return price.toLocaleString();
  },

  // 工具：获取 URL 参数
  getParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  },

  // 工具：防抖
  debounce(fn, delay = 300) {
    let timer;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => APP.init());
