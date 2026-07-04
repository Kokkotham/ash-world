/**
 * 灰烬世界 - 共享导航栏模块
 * 自动注入登录/用户区域到所有页面的 .top-nav
 * 轻量级：不依赖 CloudBase SDK，仅读 localStorage 显示状态
 * 依赖：pages/common.css 中的 .nav-right / .user-menu / .user-dropdown 样式
 */
(function () {
    'use strict';

    var PROFILE_CACHE_KEY = 'ew_profile_cache';
    var LOGGED_IN_KEY = 'ew_logged_in';
    var UID_KEY = 'ew_uid';

    // ───── 工具函数 ─────
    function isLoggedIn() {
        return localStorage.getItem(LOGGED_IN_KEY) === '1';
    }

    function getProfile() {
        try {
            var raw = localStorage.getItem(PROFILE_CACHE_KEY);
            if (raw) return JSON.parse(raw);
        } catch (e) { }
        return null;
    }

    function renderAvatar(el, name, avatar) {
        if (!el) return;
        if (avatar) {
            el.innerHTML = '<img src="' + avatar.replace(/"/g, '&quot;') + '" alt="" style="width:100%;height:100%;object-fit:cover;border-radius:50%">';
        } else {
            el.textContent = (name || '旅').charAt(0).toUpperCase();
        }
    }

    function maskPhone(phone) {
        if (!phone) return '';
        var s = phone.replace(/^\+86\s*/, '');
        if (s.length === 11) return s.slice(0, 3) + '****' + s.slice(7);
        return s;
    }

    function maskEmail(email) {
        if (!email || email.indexOf('@') === -1) return email || '';
        var parts = email.split('@');
        var name = parts[0];
        var domain = parts[1];
        var masked = name.length > 2 ? name.slice(0, 2) + '***' + name.slice(-1) : name;
        return masked + '@' + domain;
    }

    // ───── 路径判断 ─────
    function isRootPage() {
        var path = location.pathname;
        // 根目录的 index.html
        return path === '/' ||
            path.endsWith('/index.html') ||
            path.endsWith('/ash-world/') ||
            path.endsWith('/ash-world/index.html') ||
            (!path.includes('/pages/') && !path.includes('\\pages\\'));
    }

    function getLoginUrl() {
        return isRootPage() ? 'index.html?login=1' : '../index.html?login=1';
    }

    function getProfileUrl() {
        return isRootPage() ? 'pages/profile.html' : 'profile.html';
    }

    function getCharacterSheetUrl() {
        return isRootPage() ? 'pages/character-sheet.html' : 'character-sheet.html';
    }

    function getHomeUrl() {
        return isRootPage() ? 'index.html' : '../index.html';
    }

    // ───── HTML 模板 ─────
    function buildNavRightHtml() {
        return '<div class="nav-right" id="ewLoginArea">' +
            '<button class="nav-login-btn" id="ewLoginBtn" type="button">\u767B\u5F55</button>' +
            '<div class="user-menu" id="ewUserMenu" style="display:none;">' +
                '<button class="user-menu-btn" id="ewUserMenuBtn">' +
                    '<span class="user-avatar-small" id="ewNavAvatar">\u2726</span>' +
                    '<span id="ewNavName">\u65C5\u4EBA</span>' +
                '</button>' +
                '<div class="user-dropdown" id="ewUserDropdown">' +
                    '<div class="user-dropdown-header">' +
                        '<span class="user-avatar-small" id="ewDropdownAvatar">\u2726</span>' +
                        '<div class="user-dropdown-meta">' +
                            '<div class="name" id="ewDropdownName">\u65C5\u4EBA</div>' +
                            '<div class="phone" id="ewDropdownPhone">--</div>' +
                        '</div>' +
                    '</div>' +
                    '<hr class="user-dropdown-divider">' +
                    '<a class="user-dropdown-item" href="' + getProfileUrl() + '">' +
                        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>' +
                        '\u4E2A\u4EBA\u4FE1\u606F</a>' +
                    '<a class="user-dropdown-item" href="' + getCharacterSheetUrl() + '">' +
                        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>' +
                        '\u6211\u7684\u89D2\u8272\u5361</a>' +
                    '<hr class="user-dropdown-divider">' +
                    '<button class="user-dropdown-item logout-item" id="ewLogoutBtn">' +
                        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>' +
                        '\u9000\u51FA\u767B\u5F55</button>' +
                '</div>' +
            '</div>' +
        '</div>';
    }

    function buildMobileUserGroupHtml() {
        return '<div class="mobile-group" id="ewMobileUserGroup">' +
            '<div class="mobile-group-title">\u6211\u7684</div>' +
            '<a class="mobile-link" href="' + getProfileUrl() + '">\u4E2A\u4EBA\u4FE1\u606F</a>' +
            '<a class="mobile-link" href="' + getCharacterSheetUrl() + '">\u6211\u7684\u89D2\u8272\u5361</a>' +
            '<button class="mobile-link" id="ewMobileLogoutBtn" style="display:none;background:none;border:none;width:100%;text-align:left;color:#e05555">\u9000\u51FA\u767B\u5F55</button>' +
            '<button class="mobile-link" id="ewMobileLoginBtn" type="button" style="background:none;border:none;width:100%;text-align:left;color:var(--ash-gold)">\u767B\u5F55</button>' +
        '</div>';
    }

    // ───── 注入导航 ─────
    function injectNav() {
        var topNav = document.querySelector('.top-nav');
        if (topNav) {
            // 如果已有 nav-right（index.html / profile.html），不重复注入
            var existing = topNav.querySelector('.nav-right');
            if (!existing) {
                var wrapper = document.createElement('div');
                wrapper.innerHTML = buildNavRightHtml();
                topNav.appendChild(wrapper.firstChild);
            }
        }

        var navMobile = document.querySelector('.nav-mobile');
        if (navMobile) {
            var existingMobile = navMobile.querySelector('#ewMobileUserGroup') || navMobile.querySelector('#mobileUserGroup');
            if (!existingMobile) {
                var mw = document.createElement('div');
                mw.innerHTML = buildMobileUserGroupHtml();
                navMobile.appendChild(mw.firstChild);
            }
        }
    }

    // ───── 更新 UI ─────
    function updateNavUI() {
        var loggedIn = isLoggedIn();
        var profile = getProfile();
        var name = (profile && profile.displayName) ? profile.displayName : '\u65C5\u4EBA';
        var avatar = (profile && profile.avatar) ? profile.avatar : '';
        var phone = (profile && profile.phone) ? profile.phone : '';
        var email = (profile && profile.email) ? profile.email : '';

        // ash-nav.js 注入的元素
        var els = {
            loginBtn: document.getElementById('ewLoginBtn'),
            userMenu: document.getElementById('ewUserMenu'),
            navName: document.getElementById('ewNavName'),
            navAvatar: document.getElementById('ewNavAvatar'),
            dropdownName: document.getElementById('ewDropdownName'),
            dropdownPhone: document.getElementById('ewDropdownPhone'),
            dropdownAvatar: document.getElementById('ewDropdownAvatar'),
            mobileLoginBtn: document.getElementById('ewMobileLoginBtn'),
            mobileLogoutBtn: document.getElementById('ewMobileLogoutBtn')
        };

        // index.html / profile.html 已有的元素（兼容）
        var existing = {
            loginBtn: document.getElementById('loginBtn'),
            userMenu: document.getElementById('userMenu'),
            navName: document.getElementById('userMenuName'),
            navAvatar: document.getElementById('userAvatarSmall'),
            dropdownName: document.getElementById('dropdownName'),
            dropdownPhone: document.getElementById('dropdownPhone'),
            dropdownAvatar: document.getElementById('dropdownAvatar'),
            mobileLoginBtn: document.getElementById('mobileLoginBtn'),
            mobileLogoutBtn: document.getElementById('mobileLogoutBtn')
        };

        function applyToSet(set) {
            if (loggedIn) {
                if (set.loginBtn) set.loginBtn.style.display = 'none';
                if (set.userMenu) set.userMenu.style.display = 'flex';
                if (set.navName) set.navName.textContent = name;
                if (set.dropdownName) set.dropdownName.textContent = name;
                if (set.dropdownPhone) set.dropdownPhone.textContent = email ? maskEmail(email) : (maskPhone(phone) || '\u5DF2\u767B\u5F55');
                renderAvatar(set.navAvatar, name, avatar);
                renderAvatar(set.dropdownAvatar, name, avatar);
                if (set.mobileLoginBtn) set.mobileLoginBtn.style.display = 'none';
                if (set.mobileLogoutBtn) set.mobileLogoutBtn.style.display = 'block';
            } else {
                if (set.loginBtn) { set.loginBtn.style.display = 'inline-block'; set.loginBtn.textContent = '\u767B\u5F55'; }
                if (set.userMenu) set.userMenu.style.display = 'none';
                if (set.mobileLoginBtn) set.mobileLoginBtn.style.display = 'block';
                if (set.mobileLogoutBtn) set.mobileLogoutBtn.style.display = 'none';
            }
        }

        applyToSet(els);
        applyToSet(existing);
    }

    // ───── 事件绑定 ─────
    function goLogin() {
        localStorage.setItem('ew_after_login', location.href);
        if (isRootPage()) {
            if (typeof window.openLoginModal === 'function') {
                window.openLoginModal();
                return;
            }
            var overlay = document.getElementById('loginOverlay');
            if (overlay) {
                overlay.classList.add('show');
                return;
            }
            console.warn('[ash-nav] 首页登录弹窗未初始化');
            return;
        }
        location.href = getLoginUrl();
    }

    function doLogout() {
        localStorage.removeItem(LOGGED_IN_KEY);
        localStorage.removeItem(UID_KEY);
        localStorage.removeItem(PROFILE_CACHE_KEY);
        localStorage.removeItem('ew_after_login');

        if (window.ashAuth) {
            window.ashAuth.signOut().then(function () {
                location.href = getHomeUrl();
            }).catch(function () {
                location.href = getHomeUrl();
            });
        } else {
            location.href = getHomeUrl();
        }
    }

    function bindEvents() {
        // ash-nav 注入的登录按钮
        var loginBtn = document.getElementById('ewLoginBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                goLogin();
            });
        }

        // 已有的登录按钮（index.html / profile.html）
        var existingLoginBtn = document.getElementById('loginBtn');
        if (existingLoginBtn && !existingLoginBtn._ewNavBound) {
            existingLoginBtn._ewNavBound = true;
            existingLoginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                goLogin();
            });
        }

        var goLoginBtn = document.getElementById('goLoginBtn');
        if (goLoginBtn && !goLoginBtn._ewNavBound) {
            goLoginBtn._ewNavBound = true;
            goLoginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                goLogin();
            });
        }

        // 下拉菜单切换
        var menuBtn = document.getElementById('ewUserMenuBtn');
        var dropdown = document.getElementById('ewUserDropdown');
        if (menuBtn && dropdown) {
            menuBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                dropdown.classList.toggle('show');
            });
        }

        // 已有的下拉菜单
        var existingMenuBtn = document.getElementById('userMenuBtn');
        var existingDropdown = document.getElementById('userDropdown');
        if (existingMenuBtn && existingDropdown && !existingMenuBtn._ewNavBound) {
            existingMenuBtn._ewNavBound = true;
            existingMenuBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                existingDropdown.classList.toggle('show');
            });
        }

        // 退出登录
        var logoutBtn = document.getElementById('ewLogoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                if (dropdown) dropdown.classList.remove('show');
                doLogout();
            });
        }

        var existingLogoutBtn = document.getElementById('logoutBtn');
        if (existingLogoutBtn && !existingLogoutBtn._ewNavBound) {
            existingLogoutBtn._ewNavBound = true;
            existingLogoutBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                if (existingDropdown) existingDropdown.classList.remove('show');
                doLogout();
            });
        }

        // 移动端
        var mobileLoginBtn = document.getElementById('ewMobileLoginBtn');
        if (mobileLoginBtn) {
            mobileLoginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                goLogin();
            });
        }

        var existingMobileLoginBtn = document.getElementById('mobileLoginBtn');
        if (existingMobileLoginBtn && !existingMobileLoginBtn._ewNavBound) {
            existingMobileLoginBtn._ewNavBound = true;
            existingMobileLoginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                goLogin();
            });
        }

        var mobileLogoutBtn = document.getElementById('ewMobileLogoutBtn');
        if (mobileLogoutBtn) {
            mobileLogoutBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                doLogout();
            });
        }

        var existingMobileLogoutBtn = document.getElementById('mobileLogoutBtn');
        if (existingMobileLogoutBtn && !existingMobileLogoutBtn._ewNavBound) {
            existingMobileLogoutBtn._ewNavBound = true;
            existingMobileLogoutBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                doLogout();
            });
        }

        // 点击外部关闭下拉
        document.addEventListener('click', function (e) {
            if (dropdown && dropdown.classList.contains('show')) {
                var menu = document.getElementById('ewUserMenu');
                if (menu && menu.contains(e.target)) return;
                dropdown.classList.remove('show');
            }
            if (existingDropdown && existingDropdown.classList.contains('show')) {
                var exMenu = document.getElementById('userMenu');
                if (exMenu && exMenu.contains(e.target)) return;
                existingDropdown.classList.remove('show');
            }
        });
    }

    // ───── 初始化 ─────
    function init() {
        injectNav();
        bindEvents();
        updateNavUI();

        // 跨页面同步：其他页面修改了 profile 后，storage 事件触发更新
        window.addEventListener('storage', function (e) {
            if (e.key === PROFILE_CACHE_KEY || e.key === LOGGED_IN_KEY) {
                updateNavUI();
            }
        });

        // 暴露更新函数供同页面调用
        window.ashNavUpdate = updateNavUI;

        // 如果 ashReady 可用（页面加载了 ash-init.js），等 SDK 初始化后再次更新
        if (typeof window.ashReady === 'function') {
            window.ashReady(function () {
                updateNavUI();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
