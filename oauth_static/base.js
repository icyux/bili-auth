'use strict'

async function fetchUserInfo(uid) {
	let resp = await fetch(`/proxy/user?uid=${uid}`)
	let userInfo = await resp.json()

	let origAvatarURL = userInfo['avatar']
	if (/\.jpg$/.test(origAvatarURL))
		origAvatarURL += '@60w_60h_1c_1s.webp'
	const proxiedAvatarURL = `/proxy/avatar?url=${encodeURIComponent(origAvatarURL)}`
	userInfo['avatar'] = proxiedAvatarURL

	return userInfo
}

async function headerUserDisplay() {
	const vt = localStorage['verifyToken']
	if (vt === undefined)
		return

	const uid = vt.split('.')[0];
	let userInfo = await fetchUserInfo(uid)
	document.getElementById('header-avatar').src = userInfo['avatar'];
	document.getElementById('header-username').innerText = userInfo['nickname'];
}

headerUserDisplay()
