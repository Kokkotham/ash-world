/**
 * 灰烬世界 - CloudBase 数据库操作模块
 * 依赖：window.ashApp, window.ashAuth, window.ashDb（由 ash-init.js 提供）
 */
(function () {
    'use strict';

    var COLLECTIONS = {
        USERS: 'users',
        CHARACTERS: 'characters',
        SESSIONS: 'sessions'
    };

    function friendlyError(err) {
        if (!err) return '未知错误';
        var msg = (err.message || err.errMsg || String(err)).toLowerCase();
        if (msg.indexOf('db or table not exist') !== -1 || msg.indexOf('collection not exist') !== -1) {
            return '数据库集合未创建。请前往 CloudBase 控制台创建 users、characters、sessions 三个集合。';
        }
        if (msg.indexOf('permission denied') !== -1) {
            return '权限不足：请确认已登录，或联系管理员设置安全规则为 {"read":"auth != null", "write":"auth != null"}';
        }
        if (msg.indexOf('network') !== -1 || msg.indexOf('timeout') !== -1 || msg.indexOf('请求超时') !== -1) {
            return '网络连接异常，请检查网络后重试。';
        }
        if (msg.indexOf('unauthorized') !== -1 || msg.indexOf('not login') !== -1 || msg.indexOf('please login') !== -1) {
            return '登录状态已失效，请重新登录。';
        }
        return err.message || err.errMsg || String(err);
    }

    function getUid() {
        var auth = window.ashAuth;
        if (!auth) return null;
        var user = auth.currentUser;
        if (user && user.uid) return user.uid;
        return null;
    }

    function getPhone() {
        var auth = window.ashAuth;
        if (!auth) return '';
        var user = auth.currentUser;
        if (user && user.phone_number) return user.phone_number;
        return '';
    }

    function getEmail() {
        var auth = window.ashAuth;
        if (!auth) return '';
        var user = auth.currentUser;
        if (user && user.email) return user.email;
        return '';
    }

    function getCurrentUser() {
        return window.ashAuth ? window.ashAuth.currentUser : null;
    }

    // ==================== Users ====================
    function getUserProfile(uid) {
        return new Promise(function (resolve, reject) {
            if (!window.ashDb) return reject(new Error('数据库未初始化'));
            window.ashDb.collection(COLLECTIONS.USERS).doc(uid).get()
                .then(function (res) {
                    if (res.data && res.data.length > 0) {
                        resolve(res.data[0]);
                    } else {
                        resolve(null);
                    }
                })
                .catch(function (err) { reject(new Error(friendlyError(err))); });
        });
    }

    function setUserProfile(uid, profile) {
        return new Promise(function (resolve, reject) {
            if (!window.ashDb) return reject(new Error('数据库未初始化'));
            var data = {
                uid: uid,
                displayName: profile.displayName || '',
                bio: profile.bio || '',
                avatar: profile.avatar || '',
                phone: profile.phone || getPhone(),
                updatedAt: new Date()
            };
            window.ashDb.collection(COLLECTIONS.USERS).doc(uid).set(data)
                .then(function (res) { resolve(res); })
                .catch(function (err) { reject(new Error(friendlyError(err))); });
        });
    }

    function ensureUserProfile(uid) {
        return new Promise(function (resolve, reject) {
            getUserProfile(uid)
                .then(function (profile) {
                    if (profile) {
                        resolve(profile);
                    } else {
                        var defaultProfile = {
                            displayName: '旅人',
                            bio: '',
                            avatar: '',
                            phone: getPhone()
                        };
                        setUserProfile(uid, defaultProfile)
                            .then(function () { resolve(defaultProfile); })
                            .catch(reject);
                    }
                })
                .catch(reject);
        });
    }

    // ==================== Characters ====================
    function listCharacters(uid) {
        return new Promise(function (resolve, reject) {
            if (!window.ashDb) return reject(new Error('数据库未初始化'));
            window.ashDb.collection(COLLECTIONS.CHARACTERS)
                .where({ uid: uid })
                .orderBy('updatedAt', 'desc')
                .get()
                .then(function (res) {
                    resolve(res.data || []);
                })
                .catch(function (err) { reject(new Error(friendlyError(err))); });
        });
    }

    function saveCharacter(uid, character) {
        return new Promise(function (resolve, reject) {
            if (!window.ashDb) return reject(new Error('数据库未初始化'));
            var now = new Date();
            var payload = {
                uid: uid,
                name: character.name || '未命名角色',
                race: character.race || '',
                profession: character.profession || '',
                level: character.level || 1,
                method: character.method || 'dice',
                attributes: character.attributes || {},
                core: character.core || '',
                derived: character.derived || {},
                updatedAt: now,
                createdAt: character.createdAt || now
            };
            if (character._id) {
                window.ashDb.collection(COLLECTIONS.CHARACTERS).doc(character._id).update(payload)
                    .then(resolve).catch(function (err) { reject(new Error(friendlyError(err))); });
            } else {
                payload.createdAt = now;
                window.ashDb.collection(COLLECTIONS.CHARACTERS).add(payload)
                    .then(function (res) { resolve({ _id: res.id, ...payload }); })
                    .catch(function (err) { reject(new Error(friendlyError(err))); });
            }
        });
    }

    function deleteCharacter(_id) {
        return new Promise(function (resolve, reject) {
            if (!window.ashDb) return reject(new Error('数据库未初始化'));
            window.ashDb.collection(COLLECTIONS.CHARACTERS).doc(_id).remove()
                .then(resolve)
                .catch(function (err) { reject(new Error(friendlyError(err))); });
        });
    }

    // ==================== Sessions ====================
    function listSessions(uid) {
        return new Promise(function (resolve, reject) {
            if (!window.ashDb) return reject(new Error('数据库未初始化'));
            window.ashDb.collection(COLLECTIONS.SESSIONS)
                .where({ uid: uid })
                .orderBy('createdAt', 'desc')
                .get()
                .then(function (res) { resolve(res.data || []); })
                .catch(function (err) { reject(new Error(friendlyError(err))); });
        });
    }

    function addSession(uid, session) {
        return new Promise(function (resolve, reject) {
            if (!window.ashDb) return reject(new Error('数据库未初始化'));
            var payload = {
                uid: uid,
                title: session.title || '',
                role: session.role || '',
                createdAt: new Date()
            };
            window.ashDb.collection(COLLECTIONS.SESSIONS).add(payload)
                .then(function (res) { resolve({ _id: res.id, ...payload }); })
                .catch(function (err) { reject(new Error(friendlyError(err))); });
        });
    }

    window.ashDbApi = {
        friendlyError: friendlyError,
        getUid: getUid,
        getPhone: getPhone,
        getEmail: getEmail,
        getCurrentUser: getCurrentUser,
        getUserProfile: getUserProfile,
        setUserProfile: setUserProfile,
        ensureUserProfile: ensureUserProfile,
        listCharacters: listCharacters,
        saveCharacter: saveCharacter,
        deleteCharacter: deleteCharacter,
        listSessions: listSessions,
        addSession: addSession
    };
})();
