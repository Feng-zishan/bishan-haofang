// 璧山好房 · 高德地图组件
// 板块色块 + 楼盘标注 + 触摸适配

const MapView = {
  map: null,
  AMap: null,
  zones: [],
  loupanList: [],
  markers: [],

  // 初始化地图（自动从 CONFIG 读取 Key）
  async init(containerId, apiKey) {
    const key = apiKey || (typeof CONFIG !== 'undefined' && CONFIG.amapKey) || '';
    if (!key) {
      console.warn('⚠️ 高德 Key 未配置，地图功能不可用');
      return;
    }
    await this._loadSDK(key);

    const AMap = window.AMap;
    this.AMap = AMap;

    this.map = new AMap.Map(containerId, {
      zoom: 14,
      center: [106.2315, 29.5920], // 璧山区中心
      mapStyle: 'amap://styles/light',
      resizeEnable: true,
      touchZoom: true,
      dragEnable: true
    });

    // 加载数据
    await this._loadData();

    // 绘制板块色块
    this._drawZones();

    // 添加楼盘标注
    this._addMarkers();
  },

  // 加载高德 SDK
  _loadSDK(apiKey) {
    return new Promise((resolve, reject) => {
      if (window.AMap) { resolve(); return; }
      const script = document.createElement('script');
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${apiKey}&plugin=AMap.Polygon`;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  },

  // 加载板块和楼盘数据
  async _loadData() {
    try {
      const [zonesResp, loupanResp] = await Promise.all([
        fetch('/shared/bishan_zones.json'),
        fetch('/shared/loupan_list.json')
      ]);
      const zonesData = await zonesResp.json();
      const loupanData = await loupanResp.json();
      this.zones = zonesData.zones || [];
      this.loupanList = loupanData.loupanList || [];
    } catch (e) {
      console.error('地图数据加载失败:', e);
    }
  },

  // 绘制板块色块
  _drawZones() {
    if (!this.AMap) return;

    this.zones.forEach(zone => {
      const polygon = new this.AMap.Polygon({
        path: zone.boundary,
        fillColor: zone.color,
        fillOpacity: 0.15,
        strokeColor: zone.color,
        strokeWeight: 2,
        strokeOpacity: 0.6,
        zIndex: 10
      });

      polygon.on('click', () => {
        this._showZoneInfo(zone);
      });

      this.map.add(polygon);

      // 板块名称标签
      const marker = new this.AMap.Marker({
        position: zone.center,
        content: `<div style="
          background:${zone.color};color:white;padding:2px 10px;
          border-radius:12px;font-size:12px;font-weight:500;
          white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,0.15);
        ">${zone.name}</div>`,
        offset: new this.AMap.Pixel(-30, -12),
        zIndex: 20
      });
      this.map.add(marker);
    });
  },

  // 添加楼盘标注
  _addMarkers() {
    if (!this.AMap) return;

    this.loupanList.forEach(lp => {
      if (!lp.coords) return;

      const priceText = lp.avgPrice < 6000
        ? `${lp.avgPrice}元/㎡`
        : `${(lp.avgPrice / 1000).toFixed(1)}k`;

      const marker = new this.AMap.Marker({
        position: lp.coords,
        content: `<div class="map-marker" style="
          background:white;padding:4px 10px;
          border-radius:14px;font-size:11px;
          box-shadow:0 2px 8px rgba(0,0,0,0.15);
          border:2px solid var(--green-primary, #16A085);
          white-space:nowrap;cursor:pointer;
          font-weight:500;
        ">${lp.name.slice(0, 6)} ${priceText}</div>`,
        offset: new this.AMap.Pixel(-40, -16),
        zIndex: 30
      });

      marker.on('click', () => {
        APP.goTo('screen-detail');
        // TODO: 传递楼盘 ID 加载详情
      });

      this.map.add(marker);
      this.markers.push(marker);
    });
  },

  // 显示板块信息
  _showZoneInfo(zone) {
    if (!this.AMap) return;

    const infoWindow = new this.AMap.InfoWindow({
      content: `<div style="padding:12px;max-width:220px;">
        <h4 style="margin:0 0 6px;color:${zone.color};">${zone.name} ${zone.alias ? '(' + zone.alias + ')' : ''}</h4>
        <p style="margin:0 0 4px;font-size:13px;color:#666;">${zone.description}</p>
        <div style="display:flex;gap:4px;flex-wrap:wrap;">
          ${(zone.tags || []).map(t => `<span style="font-size:11px;background:#E8F8F5;color:#16A085;padding:1px 6px;border-radius:8px;">${t}</span>`).join('')}
        </div>
      </div>`,
      offset: new this.AMap.Pixel(0, -30)
    });

    infoWindow.open(this.map, zone.center);
  },

  // 过滤显示楼盘
  filterByZone(zoneId) {
    // TODO: 实现板块筛选
  }
};
