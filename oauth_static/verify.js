'use strict';

var redirect;
var vid;
var step = 0;
const finalStep = 2;

async function generateRequest() {
	let req = await fetch('/api/verify', {
		method: 'POST',
	});

	vid = await req.text();
	if (req.status == 201) {
		return vid;
	}

	return null;
}

async function checkRequestState() {
	let req = await fetch(`/api/verify/${vid}`);
	if (req.status == 202)
		return {status: 'waiting'};
	if (req.status == 404)
		return {status: 'timeout'};
	if (req.status == 200) {
		let result = await req.json();
		localStorage['verifyToken'] = result['token']
		return {
			status: 'succ',
			info: result,
		};
	}
}

async function init() {
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

	redirect = arg['redirect'];
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

async function startVerify() {
	setButtonDisable(true);
	const vid = await generateRequest();

	if (vid) {
		document.getElementById('challenge-msg').innerText = `/auth ${vid}`;
		nextStep();
	}
	else
		alert('获取验证错误。请稍侯再试。');

	setButtonDisable(false);
}

async function checkVerify() {
	setButtonDisable(true);
	let result = await checkRequestState(vid);
	if (result.status !== 'succ') {
		alert('暂未获取到验证用户信息，请稍后再试');
		setButtonDisable(false);
		return;
	}

	let uid = result.info['uid'];
	await setUserInfo(uid);
	nextStep();
	setButtonDisable(false);
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

function redirect2origin() {
	if (redirect === undefined) redirect = '/';
	window.location.href = redirect;
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
