/* 灰烬世界 — CloudBase 初始化模块
 * 在所有页面中，在 tcb-sdk.js 之后、ash-db.js 之前加载 */

(function() {
  'use strict';

  if (typeof cloudbase === 'undefined') {
    console.error('[ASH_INIT] CloudBase SDK 未加载');
    return;
  }

  var app = cloudbase.init({
    env: 'ew-prod-d0gciqy00757cc7dc',
    region: 'ap-shanghai'
  });

  var auth = app.auth({ persistence: 'local' });

  window.ashApp  = app;
  window.ashAuth = auth;

  console.log('[ASH_INIT] CloudBase 已初始化, 环境: ew-prod-d0gciqy00757cc7dc');
})();
