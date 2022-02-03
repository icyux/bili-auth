'use strict';

var cid;
var redirect;
var code;
var step = 0;
const finalStep = 3;

async function getApplication(cid) {
	let req = await fetch(`/oauth/application/${cid}`);
	if (req.status != 200)
		return null;

	let resp = await req.json();
	return resp;
}

async function generateRequest() {
	let req = await fetch(`/oauth/verify?client_id=${cid}`, {
		method: 'POST',
	});

	let result = await req.text();
	if (req.status == 201) {
		return [result, 'required'];
	}

	if (req.status == 200) {
		return [result, 'direct'];
	}

	return [null, 'err'];
}

async function checkRequestState() {
	let req = await fetch(`/oauth/verify/${code}`);
	if (req.status == 202)
		return {status: 'waiting'};
	if (req.status == 404)
		return {status: 'timeout'};
	if (req.status == 200) {
		let result = await req.json();
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

	let appInfo = await getApplication(arg['client_id']);
	if (appInfo === null) {
		document.getElementById('pending').innerText = '此应用不存在，请咨询应用管理者。';
		return;
	}

	redirect = arg['redirect_uri'];
	if (redirect === undefined) {
		document.getElementById('pending').innerText = '回调 URL 未指定，请咨询应用管理者';
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

async function startVerify() {
	setButtonDisable(true);
	let authState;
	[code, authState] = await generateRequest();
	if (authState === 'direct') {
		nextStep();
		checkVerify();
	}
	else if (code) {
		document.getElementById('challenge-msg').innerText = `auth(${code})`;
		nextStep();
	}
	else
		alert('获取验证错误。');

	setButtonDisable(false);
}

async function checkVerify() {
	setButtonDisable(true);
	let result = await checkRequestState(code);
	if (result.status !== 'succ') {
		alert('暂未获取到验证用户信息，请稍后再试');
		setButtonDisable(false);
		return;
	}

	let info = result.info;
	let avatarURL = info['avatar'];
	if (/\.jpg$/.test(avatarURL))
		avatarURL += '@60w_60h_1c_1s.webp';
	document.getElementById('avatar').src = `/proxy/avatar?url=${encodeURIComponent(avatarURL)}`;
	document.getElementById('user-name').innerText = info['nickname'];
	document.getElementById('bio').innerText = info['bio'];
	nextStep();
	setButtonDisable(false);
}

function redirectCallback() {
	if (/=/.test(redirect))
		redirect += '&';
	if (!/\?/.test(redirect))
		redirect += '?';

	window.location.href = redirect + `code=${code}`;
}

init();
