'use strict'

async function fetchUserInfo(uid) {
	const vt = localStorage['verifyToken']
	let resp = await fetch(`/api/user`,{
		headers: {
			'Authorization': `BUTKN ${vt}`,
		},
	})
	let userInfo = await resp.json()

	let origAvatarURL = userInfo['avatar']
	if (/\.jpg$/.test(origAvatarURL))
		userInfo['avatar'] = `${origAvatarURL}@60w_60h_1c_1s.webp`

	return userInfo
}

async function setUserInfo(uid) {
	const user = await fetchUserInfo(uid);
	const bio = user.bio === '' ? '（未设置个性签名）' : user.bio;
	try {
		document.getElementById('avatar').src = user.avatar;
		document.getElementById('user-name').innerText = user.name;
		document.getElementById('bio').innerText = bio;
	}
	catch (TypeError) {
		// pass
	}
}

async function headerUserDisplay() {
	const showDisplay = () => document.getElementById('user-display').hidden = false
	const vt = localStorage['verifyToken']
	if (vt === undefined) {
		showDisplay()
		return
	}

	const [uid, vid, expire, sign] = vt.split('.')
	const curTs = Math.floor(Date.now() / 1000)
	if (curTs > Number(expire)) {
		showDisplay()
		return
	}

	let userInfo = await fetchUserInfo(uid)
	document.getElementById('header-avatar').src = userInfo['avatar']
	document.getElementById('header-username').innerText = userInfo['name']
	showDisplay()
	document.getElementById('user-display').onclick = () => location.href = '/user'
}

async function loginRedirect() {
	window.location.href = '/verify'
}

if (!/\/verify$/.test(window.location.pathname))
	headerUserDisplay()
