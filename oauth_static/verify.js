'use strict';

var redirect;
var vid;
var token;
var step = 0;
const finalStep = 2;

async function generateRequest() {
	const [platform, browser] = parseUserAgent()
	let mergedUA = `${platform};${browser}`
	let req = await fetch('/api/verify', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			'ua': mergedUA,
		}),
	});

	let data = await req.json();
	if (req.status == 201) {
		return [data['vid'], data['token']];
	}

	return null;
}

async function checkRequestState() {
	let req = await fetch(`/api/verify/${vid}`, {
		headers: {
			'Authorization': `Bearer ${token}`,
		},
	});
	if (req.status == 202)
		return {status: 'waiting'};
	if (req.status == 404 || req.status == 403)
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
	[vid, token] = await generateRequest();

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
	const user = await fetchUserInfo(uid);
	document.getElementById('avatar').src = user.avatar;
	document.getElementById('user-name').innerText = user.nickname;
	document.getElementById('bio').innerText = user.bio;
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
