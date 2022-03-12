'use strict';

var cid;
var redirect;
var vid;
var code;
var authHeader;
var step = 0;
const finalStep = 2;

async function getApplication(cid) {
	let req = await fetch(`/oauth/application/${cid}`);
	if (req.status != 200)
		return null;

	let resp = await req.json();
	return resp;
}

async function init() {
	const tkn = localStorage['verifyToken'];
	if (tkn === undefined) {
		verifyRedirect();
		return;
	}
	const [uid, vid, expire, sign] = tkn.split('.');
	let currTs = Math.floor(new Date().getTime() / 1000);
	if (expire < currTs) {
		localStorage.removeItem('verifyToken');
		verifyRedirect();
		return;
	}
	authHeader = {'Authorization': `Bearer ${tkn}`};

	await setUserInfo(uid);

	let arg = {};
	try {
		let queryArgs = window.location.href.split('?')[1].split('&');
		for (let kv of queryArgs) {
			let [k, v] = kv.split('=').map(decodeURIComponent);
			arg[k] = v;
		}
		console.log(arg);
	}
	catch (TypeError) {
		// pass
	}

	let appInfo = await getApplication(arg['client_id']);
	if (appInfo === null) {
		document.getElementById('pending').innerText = '此应用不存在，请咨询应用管理者。';
		return;
	}

	redirect = arg['redirect_uri'];
	if (redirect === undefined) {
		document.getElementById('pending').innerText = '重定向 URL 未指定，请咨询应用管理者';
		return;
	}

	cid = appInfo['cid'];

	document.getElementById('app-id').innerText = cid;
	document.getElementById('app-name').innerText = appInfo['name'];
	document.getElementById('app-url').innerText = appInfo['url'];
	nextStep();
}

function nextStep() {
	step++;
	document.getElementById(`step-${step-1}`).hidden = true;
	document.getElementById(`step-${step}`).hidden = false;
}

function setButtonDisable(state) {
	for (let e of document.getElementsByClassName('next-step'))
		e.disabled = state;
}

async function queryExistedAccCode() {
	let resp = await fetch(`/api/session?client_id=${cid}`, {
		headers: authHeader,
	});
	if (resp.status === 403) {
		alert('查询会话失败。');
		return;
	}

	let sessions = await resp.json();
	if (sessions.length > 0) {
		return sessions[0].accCode;
	}
	else {
		return null;
	}
}

async function createSession() {
	const resp = await fetch(`/api/session?client_id=${cid}`, {
		method: 'post',
		headers: authHeader,
	});
	if (resp.status === 403) {
		alert('授权超时，请重试。');
		return;
	}
	const result = await resp.json();
	return result['accessCode'];
}

async function authorizeApp() {
	const existedCode = await queryExistedAccCode();
	if (existedCode) {
		code = existedCode;
	}
	else {
		code = await createSession();
	}
	redirectCallback();
}

async function setUserInfo(uid) {
	let resp = await fetch(`/proxy/user?uid=${uid}`);
	let userInfo = await resp.json();
	let avatarURL = userInfo['avatar'];
	if (/\.jpg$/.test(avatarURL))
		avatarURL += '@60w_60h_1c_1s.webp';
	document.getElementById('avatar').src = `/proxy/avatar?url=${encodeURIComponent(avatarURL)}`;
	document.getElementById('user-name').innerText = userInfo['nickname'];
	document.getElementById('bio').innerText = userInfo['bio'];
}

function redirectCallback() {
	if (/=/.test(redirect))
		redirect += '&';
	if (!/\?/.test(redirect))
		redirect += '?';

	window.location.href = redirect + `code=${code}`;
}

function verifyRedirect() {
	const callback = window.location.pathname + window.location.search;
	const callbackEncoded = encodeURIComponent(callback);
	window.location.href = `/verify?redirect=${callbackEncoded}`;
}

async function copyVerifyCode() {
	try {
		await navigator.clipboard.writeText(document.getElementById('challenge-msg').innerText);
		alert('已复制内容到剪贴板。现在您可以在私信页面直接粘贴。');
	}
	catch (e) {
		alert('复制失败，您的浏览器不支持 Clipboard API 或拒绝剪贴板访问。请手动复制消息。');
	}
}

init();
