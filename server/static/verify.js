'use strict';

var redirect;
var vid;
var token;
var botUid;
var step = 'intro';
var expireAt, duration, timerRunId;

async function generateRequest() {
	let ua = await parseUserAgent()
	let req = await fetch('/api/verify', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			'ua': ua,
		}),
	});

	let data = await req.json();
	if (req.status == 201) {
		const curTs = Math.floor(new Date().getTime() / 1000)
		expireAt = data['expire'];
		duration = 360;
		timerRunId = setInterval(refreshRemainTime, 1000);
		return data;
	}

	return null;
}

async function checkRequestState() {
	let req = await fetch(`/api/verify/${vid}`, {
		headers: {
			'Authorization': `BUTKN ${token}`,
		},
	});
	if (req.status == 202)
		return {status: 'waiting'};
	if (req.status == 404 || req.status == 403)
		return {status: 'timeout'};
	if (req.status == 500)
		return {status: 'error'};
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

function nextStep(nxtStep) {
	document.getElementById(step).hidden = true;
	document.getElementById(nxtStep).hidden = false;
	step = nxtStep;
}

function setButtonDisable(state) {
	for (let e of document.getElementsByClassName('next-step'))
		e.disabled = state;
}

async function startVerify(authType) {
	setButtonDisable(true);
	document.querySelectorAll("button.option").forEach((btn) => btn.disabled = true);

	const result = await generateRequest();

	if (result) {
		[vid, token, botUid] = [result.vid, result.token, result.botInfo.uid];
		document.getElementById('challenge-msg').innerText = `确认授权 ${vid}`;
		if (authType === 'app') {
			if (isMobile()) authType = 'applink';
			else {
				authType = 'qrscan';
				document.getElementById('qrcode').src = result.botInfo.qrcode;
			}
		}
		nextStep('auth-main');
		document.getElementById(`auth-by-${authType}`).hidden = false;
	}
	else
		alert('获取验证错误。请稍侯再试。');

	setButtonDisable(false);
}

async function checkVerify() {
	setButtonDisable(true);
	let result = await checkRequestState(vid);
	if (result.status === 'error') {
		alert('服务内部出现错误，请稍后再试');
		setButtonDisable(false);
		return;
	}
	if (result.status !== 'succ') {
		alert('暂未获取到验证用户信息，请稍后再试');
		setButtonDisable(false);
		return;
	}

	let uid = result.info['uid'];
	try {
		await setUserInfo(uid);
	}
	catch (e) {
		alert('获取用户信息失败，请稍后再试；若多次出错您可以向开发者反馈。');
		setButtonDisable(false);
		return;	
	}
	nextStep('finish');
	setButtonDisable(false);
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

function openInApp() {
	window.location.href = `bilibili://space/${botUid}`;
}

function openInNewTab() {
	window.open(`https://message.bilibili.com/#/whisper/mid${botUid}`);
}

function refreshRemainTime() {
	const curTs = Math.floor(new Date().getTime() / 1000)
	const remainSec = expireAt - curTs
	if (remainSec < 0) {
		document.getElementById('remain').innerText = '本次操作已超时。'
		clearInterval(timerRunId)
		return
	}
	const percent = (remainSec / duration * 100).toFixed(2)
	document.getElementById('remain').style = `--remain: ${percent}%`
	document.getElementById('remain-timer').innerText = `${remainSec}秒`
}

init();
