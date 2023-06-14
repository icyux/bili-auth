'use strict'

async function fetchAppInfo() {
	await Promise.all([
		fetchAuthorizedApps(),
		fetchCreatedApps(),
	])
}

async function fetchAuthorizedApps() {
	let vt = localStorage.verifyToken
	let resp = await fetch('/api/user/apps/authorized', {
		headers: {
			'Authorization': `BUTKN ${vt}`,
		},
	})
	let authorizedApps = await resp.json()
	let tpl = document.getElementById('app-tpl')
	for (let app of authorizedApps) {
		tpl.content.querySelector('.app-icon').src = app['icon']
		tpl.content.querySelector('.app-name').innerText = app['name']
		tpl.content.querySelector('button').innerText = '撤销授权'
		tpl.content.querySelector('button').onclick = () => revokeAuthorization(app['cid'])
		let row = document.importNode(tpl.content, true)
		document.getElementById('authorized-apps').appendChild(row)
	}
}

async function fetchCreatedApps() {
	let vt = localStorage.verifyToken
	let resp = await fetch('/api/user/apps/created', {
		headers: {
			'Authorization': `BUTKN ${vt}`,
		},
	})
	let createdApps = await resp.json()
	let tpl = document.getElementById('app-tpl')
	for (let app of createdApps) {
		tpl.content.querySelector('.app-icon').src = app['icon']
		tpl.content.querySelector('.app-name').innerText = app['name']
		tpl.content.querySelector('button').innerText = '删除应用'
		// todo
		// tpl.content.querySelector('button').onclick = ...
		let row = document.importNode(tpl.content, true)
		document.getElementById('authorized-apps').appendChild(row)
	}
}

async function revokeAuthorization(cid) {
	// todo: implement the API on backend
	return
	if (confirm('确认撤销对该应用的授权？')) {
		const vt = localStorage.verifyToken
		await fetch(`/path/to/api`, {
			method: 'DELETE',
			headers: {
				'Authorization': `BUTKN ${vt}`,
			},
		})
	}
}

function switchOption(event) {
	const OptionCount = 2
	const matchResult = /opt-(\d+)/.exec(event.target.id)
	if (matchResult === null)
		return

	const optionId = matchResult[1]
	for (let i = 0; i < OptionCount; i++) {
		document.getElementById(`opt-${i}`).classList.remove('selected')
		document.getElementById(`area-${i}`).hidden = true
	}
	document.getElementById(`opt-${optionId}`).classList.add('selected')
	document.getElementById(`area-${optionId}`).hidden = false
}

async function init() {
	document.getElementById('navigator').onclick = (e) => switchOption(e)
	await setUserInfo()
	await fetchAppInfo()
}

init()
