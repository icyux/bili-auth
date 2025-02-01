'use strict'

async function fetchUserInfo() {
	const vt = localStorage['verifyToken']
	let resp = await fetch(`/api/user`,{
		headers: {
			'Authorization': `BUTKN ${vt}`,
		},
	})
	if (resp.status === 403) {
		return null
	}

	let userInfo = await resp.json()

	let origAvatarURL = userInfo['avatar']
	if (/\.jpg$/.test(origAvatarURL))
		userInfo['avatar'] = `${origAvatarURL}@60w_60h_1c_1s.webp`

	return userInfo
}

async function setUserInfo() {
	const user = await fetchUserInfo();
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

	const userInfo = await fetchUserInfo()
	if (userInfo === null) {
		localStorage.removeItem('verifyToken')
	}
	else {
		document.getElementById('header-avatar').src = userInfo['avatar']
		document.getElementById('header-username').innerText = userInfo['name']
		document.getElementById('user-display').onclick = () => location.href = '/user'
	}
	showDisplay()
}

function loginRedirect() {
	window.location.href = '/verify'
}

if (!/\/(verify|user)$/.test(window.location.pathname))
	headerUserDisplay()
