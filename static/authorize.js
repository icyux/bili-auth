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
	authHeader = {'Authorization': `BUTKN ${tkn}`};

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
		document.getElementById('pending').innerText = '回调 URL 未指定，请咨询应用管理者。';
		return;
	}

	if (redirect.indexOf(appInfo.prefix) !== 0) {
		document.getElementById('pending').innerText = '回调 URL 与预设前缀不匹配，请咨询应用管理者。';
		return;	
	}

	cid = appInfo['cid'];

	document.getElementById('app-id').innerText = cid;
	document.getElementById('app-name').innerText = appInfo['name'];
	document.getElementById('app-url').href = appInfo['link'];
	document.getElementById('app-url').innerText = appInfo['link'];
	document.getElementById('app-icon').src = appInfo['icon'];
	document.getElementById('app-desc').innerText = appInfo['desc'];
	document.getElementById('redirect-uri').innerText = redirect;
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
		throw new Error('Invalid token');
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
	document.getElementById('authorize').disabled = true;
	document.getElementById('authorize').innerText = '正在授权...';
	var existedCode;
	try {
		existedCode = await queryExistedAccCode();
	}
	catch (e) {
		alert('无效的 Token。请尝试重新验证。');
		verifyRedirect();
		return;
	}
	if (existedCode) {
		code = existedCode;
	}
	else {
		code = await createSession();
	}
	redirectCallback();
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

init();
