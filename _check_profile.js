<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人主页 — 灰烬世界</title>
    <link rel="stylesheet" href="common.css">
    <style>
        :root {
            --panel-bg: rgba(14,18,24,0.55);
            --panel-border: rgba(201,168,76,0.12);
        }
        .profile-wrapper {
            max-width: 780px; margin: 0 auto;
            padding: 100px 20px 60px;
            display: flex; flex-direction: column; gap: 24px;
        }
        /* ── 头像区 ── */
        .profile-header {
            text-align: center; padding: 20px 0 8px;
        }
        .avatar-circle {
            width: 88px; height: 88px; border-radius: 50%;
            margin: 0 auto 16px;
            background: rgba(201,168,76,0.08);
            border: 2px solid rgba(201,168,76,0.25);
            background-size: cover; background-position: center;
            position: relative; cursor: pointer;
            transition: border-color 0.3s, box-shadow 0.3s;
            display: flex; align-items: center; justify-content: center;
            overflow: hidden;
        }
        .avatar-circle:hover {
            border-color: var(--ash-gold);
            box-shadow: 0 0 20px rgba(201,168,76,0.15);
        }
        .avatar-placeholder {
            color: var(--ash-dim); font-size: 2rem;
            pointer-events: none;
        }
        .avatar-upload-hint {
            position: absolute; inset: 0;
            display: flex; align-items: center; justify-content: center;
            background: rgba(0,0,0,0.5); opacity: 0;
            transition: opacity 0.3s; border-radius: 50%;
            color: var(--ash-gold); font-size: 0.72rem;
            letter-spacing: 0.06em;
        }
        .avatar-circle:hover .avatar-upload-hint { opacity: 1; }
        #avatarInput { display: none; }
        .profile-name {
            font-family: 'Cinzel', serif;
            font-size: 1.6rem; font-weight: 700;
            color: var(--ash-gold);
            letter-spacing: 0.1em;
            margin-bottom: 4px;
        }
        .profile-phone {
            font-size: 0.78rem; color: var(--ash-dim);
            letter-spacing: 0.06em; margin-bottom: 6px;
        }
        .profile-bio {
            font-size: 0.85rem; color: var(--ash-dim);
            letter-spacing: 0.04em; opacity: 0.7;
            max-width: 400px; margin: 0 auto;
        }
        .edit-link {
            display: inline-block; margin-top: 12px;
            padding: 6px 18px;
            border: 1px solid rgba(201,168,76,0.2);
            border-radius: 2px; color: var(--ash-gold);
            font-size: 0.75rem; letter-spacing: 0.08em;
            background: rgba(201,168,76,0.04);
            cursor: pointer; transition: all 0.3s;
            text-decoration: none;
        }
        .edit-link:hover {
            background: rgba(201,168,76,0.12);
            border-color: var(--ash-gold);
        }

        /* ── 面板通用 ── */
        .panel {
            background: var(--panel-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--panel-border);
            border-radius: 8px; padding: 28px 24px;
        }
        .panel::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(201,168,76,0.15), transparent);
            pointer-events: none;
        }
        .panel { position: relative; overflow: hidden; }
        .panel-title {
            font-family: 'Cinzel', serif;
            font-size: 1.1rem; font-weight: 700;
            color: var(--ash-gold); letter-spacing: 0.08em;
            margin-bottom: 16px; display: flex; align-items: center; gap: 10px;
        }
        .panel-title .icon { font-size: 1.1rem; }

        /* ── 角色卡网格 ── */
        .char-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 14px;
        }
        .char-card {
            background: rgba(201,168,76,0.04);
            border: 1px solid rgba(201,168,76,0.1);
            border-radius: 6px; padding: 16px;
            cursor: pointer; transition: all 0.3s;
            text-decoration: none; display: block;
        }
        .char-card:hover {
            background: rgba(201,168,76,0.08);
            border-color: var(--ash-gold);
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }
        .char-card .char-name {
            font-family: 'Cinzel', serif;
            font-size: 0.95rem; font-weight: 700;
            color: var(--ash-gold); letter-spacing: 0.06em;
            margin-bottom: 6px;
        }
        .char-card .char-meta {
            font-size: 0.72rem; color: var(--ash-dim);
            letter-spacing: 0.04em; display: flex; gap: 12px;
            flex-wrap: wrap;
        }
        .char-card .char-date {
            font-size: 0.65rem; color: rgba(255,255,255,0.2);
            margin-top: 8px; letter-spacing: 0.04em;
        }
        .new-char-btn {
            display: flex; align-items: center; justify-content: center;
            gap: 8px; padding: 14px;
            border: 1px dashed rgba(201,168,76,0.2);
            border-radius: 6px; color: var(--ash-dim);
            font-size: 0.82rem; letter-spacing: 0.06em;
            cursor: pointer; transition: all 0.3s;
            background: transparent;
        }
        .new-char-btn:hover {
            border-color: var(--ash-gold); color: var(--ash-gold);
            background: rgba(201,168,76,0.04);
        }

        /* ── 游戏记录 ── */
        .session-list { display: flex; flex-direction: column; gap: 10px; }
        .session-item {
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 16px;
            background: rgba(201,168,76,0.03);
            border-radius: 4px;
        }
        .session-item .session-name {
            font-size: 0.85rem; color: var(--ash-text);
            letter-spacing: 0.04em;
        }
        .session-item .session-date {
            font-size: 0.7rem; color: var(--ash-dim);
            white-space: nowrap;
        }
        .session-item .session-role {
            font-size: 0.68rem; color: var(--ash-gold);
            margin-left: auto; margin-right: 12px;
            opacity: 0.7;
        }

        /* ── 统计数字 ── */
        .stat-row {
            display: flex; gap: 24px; flex-wrap: wrap;
        }
        .stat-item { flex: 1; min-width: 100px; text-align: center; }
        .stat-item .stat-num {
            font-family: 'Cinzel', serif;
            font-size: 1.8rem; font-weight: 700;
            color: var(--ash-gold); letter-spacing: 0.06em;
        }
        .stat-item .stat-label {
            font-size: 0.72rem; color: var(--ash-dim);
            letter-spacing: 0.04em; margin-top: 4px;
        }

        /* ── 空状态 ── */
        .empty-state {
            text-align: center; padding: 32px 20px;
            color: var(--ash-dim); font-size: 0.85rem;
            letter-spacing: 0.04em; opacity: 0.6;
        }
        .empty-state .empty-icon { font-size: 2rem; margin-bottom: 8px; display: block; }

        /* ── 编辑弹窗（复用 index 样式） ── */
        .profile-overlay {
            position: fixed; inset: 0; z-index: 500;
            display: flex; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none;
            transition: opacity 0.25s ease;
        }
        .profile-overlay.show { opacity: 1; pointer-events: auto; }
        .login-backdrop {
            position: absolute; inset: 0;
            background: rgba(0,0,0,0.6);
        }
        .profile-card {
            position: relative; width: 360px; max-width: 90vw;
            background: linear-gradient(160deg, rgba(18,22,30,0.97) 0%, rgba(10,14,20,0.98) 100%);
            border: 1px solid rgba(201,168,76,0.2);
            border-radius: 4px;
            box-shadow: 0 16px 48px rgba(0,0,0,0.6);
            padding: 32px 28px 24px;
            backdrop-filter: blur(24px);
        }
        .profile-card h2 {
            font-family: 'Cinzel', serif;
            font-size: 1.1rem; font-weight: 700;
            color: var(--ash-gold); letter-spacing: 0.08em;
            margin-bottom: 20px;
        }
        .profile-card label {
            display: block; font-size: 0.72rem;
            color: var(--ash-dim); margin-bottom: 6px;
            letter-spacing: 0.06em;
        }
        .profile-card input, .profile-card textarea {
            width: 100%; margin-bottom: 14px;
            border: 1px solid rgba(201,168,76,0.2);
            border-radius: 2px;
            background: rgba(0,0,0,0.3);
            color: var(--ash-dim);
            font-size: 0.82rem; padding: 10px 12px;
            font-family: 'Noto Serif SC', serif;
            outline: none; transition: border-color 0.3s;
        }
        .profile-card input:focus, .profile-card textarea:focus {
            border-color: var(--ash-gold);
        }
        .profile-card textarea {
            resize: vertical; min-height: 60px;
        }
        .profile-save-btn {
            display: block; width: 100%; padding: 11px;
            background: linear-gradient(135deg, rgba(201,168,76,0.2), rgba(180,140,50,0.15));
            border: 1px solid rgba(201,168,76,0.35);
            border-radius: 2px; color: var(--ash-gold);
            font-size: 0.82rem; letter-spacing: 0.1em; cursor: pointer;
            transition: all 0.25s ease;
        }
        .profile-save-btn:hover {
            background: linear-gradient(135deg, rgba(201,168,76,0.3), rgba(180,140,50,0.25));
            border-color: var(--ash-gold);
        }
        .profile-save-btn:disabled { cursor: not-allowed; opacity: 0.4; }
        .login-close {
            position: absolute; top: 10px; right: 14px;
            background: none; border: none;
            color: var(--ash-dim); font-size: 1.3rem;
            cursor: pointer; transition: color 0.2s;
        }
        .login-close:hover { color: var(--ash-gold); }
        .profile-success { color: #8cd4b8; font-size: 0.72rem; text-align: center; margin-top: 8px; opacity: 0; transition: opacity 0.3s ease; }
        .profile-success.visible { opacity: 1; }
        .login-error { color: #d44; font-size: 0.72rem; margin-top: 8px; text-align: center; min-height: 1.2em; }
    </style>
</head>
<body>
    <nav class="top-nav" id="page-header">
        <div class="nav-brand"><a href="../index.html" style="color:inherit;text-decoration:none;">灰烬世界</a></div>
        <div class="nav-links">
            <div class="nav-item"><a href="worldview.html">世界设定</a></div>
            <div class="nav-item"><a href="rules.html">规则书</a></div>
            <div class="nav-item"><a href="character-sheet.html">角色卡</a></div>
            <div class="nav-item">
                <a href="../index.html" style="color:var(--ash-gold);">首页</a>
            </div>
        </div>
    </nav>

    <div class="profile-wrapper">
        <!-- 头像 + 基本信息 -->
        <div class="profile-header">
            <div class="avatar-circle" id="avatarCircle" title="点击上传头像">
                <span class="avatar-placeholder" id="avatarPlaceholder">?</span>
                <span class="avatar-upload-hint">更换头像</span>
            </div>
            <input type="file" id="avatarInput" accept="image/*">
            <div class="profile-name" id="displayName">未设置</div>
            <div class="profile-phone" id="phoneDisplay"></div>
            <div class="profile-bio" id="bioDisplay"></div>
            <a class="edit-link" id="editProfileBtn" href="javascript:void(0)">编辑资料</a>
        </div>

        <!-- 统计 -->
        <div class="panel" id="statsPanel">
            <div class="panel-title"><span class="icon">&#9733;</span>数据统计</div>
            <div class="stat-row">
                <div class="stat-item"><span class="stat-num" id="charCount">0</span><span class="stat-label">角色卡</span></div>
                <div class="stat-item"><span class="stat-num" id="sessionCount">0</span><span class="stat-label">游戏记录</span></div>
                <div class="stat-item"><span class="stat-num">-</span><span class="stat-label">成就点数</span></div>
            </div>
        </div>

        <!-- 我的角色卡 -->
        <div class="panel" id="charsPanel">
            <div class="panel-title"><span class="icon">&#9876;</span>我的角色卡</div>
            <div class="char-grid" id="charGrid">
                <div class="empty-state"><span class="empty-icon">&#9876;</span>还没有角色卡</div>
            </div>
            <a class="new-char-btn" href="character-sheet.html" style="margin-top:16px;display:flex;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                创建新角色
            </a>
        </div>

        <!-- 游戏记录 -->
        <div class="panel" id="sessionsPanel">
            <div class="panel-title"><span class="icon">&#9733;</span>游戏记录</div>
            <div class="session-list" id="sessionList">
                <div class="empty-state"><span class="empty-icon">&#9783;</span>还没有游戏记录</div>
            </div>
        </div>
    </div>

    <!-- 编辑弹窗 -->
    <div class="profile-overlay" id="editOverlay">
        <div class="login-backdrop" id="editBackdrop"></div>
        <div class="profile-card">
            <button class="login-close" id="editClose">&times;</button>
            <h2>编辑资料</h2>
            <label>显示名称</label>
            <input type="text" id="editName" placeholder="你在余烬中的名字" maxlength="20">
            <label>个人简介</label>
            <textarea id="editBio" placeholder="灰烬中的旅人..." maxlength="120"></textarea>
            <button class="profile-save-btn" id="editSaveBtn">保存到云端</button>
            <div class="profile-success" id="editSuccess">已保存</div>
            <div class="login-error" id="editError"></div>
        </div>
    </div>