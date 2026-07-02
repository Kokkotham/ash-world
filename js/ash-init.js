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

    function safeStringify(obj, maxLen) {
        maxLen = maxLen || 500;
        if (obj === null || obj === undefined) return '';
        if (typeof obj === 'string') return obj;
        if (typeof obj === 'number' || typeof obj === 'boolean') return String(obj);
        if (obj instanceof Error) return obj.message || String(obj);
        try {
            var json = JSON.stringify(obj);
            if (json && json.length > maxLen) json = json.slice(0, maxLen) + '...';
            return json || String(obj);
        } catch (e) {
            return String(obj);
        }
    }
    function extractErrorMessage(err) {
        if (!err) return '未知错误';
        if (typeof err === 'string') return err;
        var candidates = [
            err.message, err.errMsg, err.msg, err.errorMessage, err.errorMsg,
            err.error_description, err.description, err.reason,
            err.error && err.error.message, err.error && err.error.errMsg,
            err.data && err.data.message, err.data && err.data.errMsg, err.data && err.data.msg,
            err.response && err.response.data && err.response.data.message,
            err.response && err.response.data && err.response.data.errMsg
        ];
        for (var i = 0; i < candidates.length; i++) {
            var c = candidates[i];
            if (c && typeof c === 'string' && c.trim()) return c.trim();
        }
        if (err.message && typeof err.message === 'object') return extractErrorMessage(err.message);
        if (err.data && typeof err.data === 'object') return extractErrorMessage(err.data);
        return safeStringify(err, 300);
    }
    function friendlyError(err) {
        var raw = extractErrorMessage(err);
        var msg = raw.toLowerCase();
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
        if (msg.indexOf('invalid verification code') !== -1 || msg.indexOf('verification code') !== -1) {
            return '验证码错误或已过期，请重新获取。';
        }
        if (msg.indexOf('is not a function') !== -1) {
            return 'SDK 接口调用错误，请刷新页面或联系管理员。';
        }
        if (msg.indexOf('internal server error') !== -1 || msg.indexOf('internal error') !== -1) {
            return '服务端错误，请稍后重试或联系管理员。';
        }
        return raw;
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
