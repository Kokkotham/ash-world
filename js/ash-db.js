/* 灰烬世界 — CloudBase 数据库操作模块
 * 加载前提: cloudbase SDK 已初始化 (tcb-sdk.js)
 * 依赖: 全局变量 ashApp (CloudBase app 实例), ashAuth (auth 实例) */

(function() {
  'use strict';

  var db = null;
  var _uid = null;
  var _ready = false;

  var ASH_DB = window.ASH_DB = window.ASH_DB || {};

  function ensureDb() {
    if (db) return db;
    if (typeof cloudbase === 'undefined') throw new Error('CloudBase SDK 未加载');
    if (!window.ashApp) throw new Error('ashApp 未初始化');
    db = window.ashApp.database();
    return db;
  }

  function getUid() {
    if (_uid) return Promise.resolve(_uid);
    if (!window.ashAuth) return Promise.reject(new Error('ashAuth 未初始化'));
    return window.ashAuth.getLoginState().then(function(result) {
      var data = (result && result.data !== undefined) ? result.data : result;
      if (data && data.user) {
        _uid = data.user.uid;
        return _uid;
      }
      throw new Error('未登录');
    });
  }

  function friendlyError(err) {
    var msg = (err && (err.message || err.msg || err.errMsg || err.code)) || String(err);
    if (/Db or Table not exist|not exist|collection not found/i.test(msg)) {
      throw new Error('数据库集合未创建。请在 CloudBase 控制台建立 users、characters、sessions 三个集合。');
    }
    if (/permission denied|not authorized|auth/i.test(msg)) {
      throw new Error('数据库权限不足。请检查 CloudBase 数据库安全规则是否允许登录用户读写。');
    }
    throw new Error('云端保存失败：' + msg);
  }

  ASH_DB.ready = function() {
    if (_ready) return Promise.resolve(true);
    try {
      ensureDb();
      _ready = true;
      return Promise.resolve(true);
    } catch(e) {
      return Promise.reject(e);
    }
  };

  /* ── 用户资料 CRUD ── */

  ASH_DB.user = {
    /* 获取当前用户资料，不存在则自动创建 */
    getOrCreate: function() {
      return getUid().then(function(uid) {
        return db.collection('users').where({ uid: uid }).get().then(function(res) {
          if (res.data && res.data.length > 0) return res.data[0];
          return db.collection('users').add({
            uid: uid,
            displayName: '',
            avatar: '',
            bio: '',
            createdAt: Date.now(),
            updatedAt: Date.now()
          }).then(function(addRes) {
            return db.collection('users').doc(addRes.id).get().then(function(r) { return r.data[0]; });
          });
        });
      }).catch(friendlyError);
    },

    /* 更新用户资料 */
    update: function(fields) {
      return getUid().then(function(uid) {
        return ASH_DB.user.getOrCreate().then(function(user) {
          fields.updatedAt = Date.now();
          return db.collection('users').doc(user._id).update(fields).then(function() {
            return Object.assign({}, user, fields);
          });
        });
      }).catch(friendlyError);
    }
  };

  /* ── 角色卡 CRUD ── */

  ASH_DB.characters = {
    /* 列出当前用户所有角色卡 */
    list: function() {
      return getUid().then(function(uid) {
        return db.collection('characters').where({ uid: uid }).orderBy('updatedAt', 'desc').get().then(function(res) {
          return res.data || [];
        });
      }).catch(friendlyError);
    },

    /* 保存角色卡（创建或更新） */
    save: function(characterData) {
      return getUid().then(function(uid) {
        characterData.uid = uid;
        characterData.updatedAt = Date.now();
        if (characterData._id) {
          return db.collection('characters').doc(characterData._id).update(characterData).then(function() {
            return characterData;
          });
        }
        characterData.createdAt = Date.now();
        return db.collection('characters').add(characterData).then(function(res) {
          characterData._id = res.id;
          return characterData;
        });
      }).catch(friendlyError);
    },

    /* 删除角色卡 */
    remove: function(characterId) {
      return getUid().then(function() {
        return db.collection('characters').doc(characterId).remove();
      }).catch(friendlyError);
    },

    /* 获取单张角色卡 */
    get: function(characterId) {
      return db.collection('characters').doc(characterId).get().then(function(res) {
        return res.data && res.data[0] || null;
      }).catch(friendlyError);
    }
  };

  /* ── 游戏记录 ── */

  ASH_DB.sessions = {
    /* 记录一次游戏 */
    log: function(sessionData) {
      return getUid().then(function(uid) {
        sessionData.uid = uid;
        sessionData.createdAt = Date.now();
        return db.collection('sessions').add(sessionData).then(function(res) {
          sessionData._id = res.id;
          return sessionData;
        });
      }).catch(friendlyError);
    },

    /* 获取游戏记录列表 */
    list: function(limit) {
      limit = limit || 20;
      return getUid().then(function(uid) {
        return db.collection('sessions').where({ uid: uid }).orderBy('createdAt', 'desc').limit(limit).get().then(function(res) {
          return res.data || [];
        });
      }).catch(friendlyError);
    },

    /* 获取游戏统计 */
    stats: function() {
      return getUid().then(function(uid) {
        return db.collection('sessions').where({ uid: uid }).count().then(function(countRes) {
          return { totalSessions: countRes.total || 0 };
        });
      }).catch(friendlyError);
    }
  };

  /* ── 头像上传 ── */

  ASH_DB.uploadAvatar = function(file) {
    return getUid().then(function(uid) {
      var cloudPath = 'avatars/' + uid + '/' + Date.now() + '_' + file.name;
      return window.ashApp.uploadFile({
        cloudPath: cloudPath,
        filePath: file
      }).then(function(res) {
        return window.ashApp.getTempFileURL({ fileList: [res.fileID] }).then(function(urlRes) {
          return urlRes.fileList[0].tempFileURL;
        });
      });
    });
  };

  console.log('[ASH_DB] 数据库模块已就绪');
})();
