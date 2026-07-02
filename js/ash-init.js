/**
 * 灰烬世界 - CloudBase 共享初始化模块
 * 导出：window.ashApp, window.ashAuth, window.ashDb, window.ashReady()
 */
(function () {
    'use strict';

    var ENV_ID = 'ew-prod-d0gciqy00757cc7dc';
    var APP = null;
    var AUTH = null;
    var DB = null;
    var READY = false;
    var READY_CALLBACKS = [];

    function onReady(callback) {
        if (READY) {
            setTimeout(function () { callback(APP, AUTH, DB); }, 0);
        } else {
            READY_CALLBACKS.push(callback);
        }
    }

    function triggerReady() {
        READY = true;
        while (READY_CALLBACKS.length) {
            var cb = READY_CALLBACKS.shift();
            try { cb(APP, AUTH, DB); } catch (e) { console.error('ash-init ready callback error', e); }
        }
    }

    function friendlyError(err) {
        if (!err) return '未知错误';
        var msg = (err.message || err.errMsg || String(err)).toLowerCase();
        if (msg.indexOf('db or table not exist') !== -1 || msg.indexOf('collection not exist') !== -1) {
            return '数据库集合未创建，请联系管理员在 CloudBase 控制台创建集合。';
        }
        if (msg.indexOf('permission denied') !== -1) {
            return '权限不足，请确认已登录或联系管理员调整安全规则。';
        }
        if (msg.indexOf('network') !== -1 || msg.indexOf('timeout') !== -1 || msg.indexOf('请求超时') !== -1) {
            return '网络连接异常，请检查网络后重试。';
        }
        if (msg.indexOf('invalid phone') !== -1 || msg.indexOf('phone number') !== -1) {
            return '手机号格式不正确。';
        }
        if (msg.indexOf('invalid verification code') !== -1 || msg.indexOf('验证码') !== -1) {
            return '验证码错误或已过期，请重新获取。';
        }
        return err.message || err.errMsg || String(err);
    }

    function init() {
        if (typeof cloudbase === 'undefined') {
            console.error('[ash-init] CloudBase SDK 未加载');
            return;
        }
        try {
            APP = cloudbase.init({ env: ENV_ID });
            AUTH = APP.auth({ persistence: 'local' });
            DB = APP.database();
            window.ashApp = APP;
            window.ashAuth = AUTH;
            window.ashDb = DB;
            triggerReady();
        } catch (e) {
            console.error('[ash-init] CloudBase 初始化失败', e);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.ashReady = onReady;
    window.ashFriendlyError = friendlyError;
})();
