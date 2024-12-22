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
		let row = document.importNode(tpl.content, true)
		row.querySelector('.app-icon').src = app['icon']
		row.querySelector('.app-name').innerText = app['name']
		row.querySelector('button').innerText = '撤销授权'
		row.querySelector('button').onclick = () => revokeAuthorization(app['cid'])
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
		let row = document.importNode(tpl.content, true)
		row.querySelector('.app-icon').src = app['icon']
		row.querySelector('.app-name').innerText = app['name']
		row.querySelector('button').innerText = '删除应用'
		row.querySelector('button').onclick = () => deleteApplication(app['cid'])
		document.getElementById('created-apps').appendChild(row)
	}
}

async function revokeAuthorization(cid) {
	if (confirm('确认撤销对该应用的授权？')) {
		const vt = localStorage.verifyToken
		let resp = await fetch(`/api/user/apps/authorized?cid=${cid}`, {
			method: 'DELETE',
			headers: {
				'Authorization': `BUTKN ${vt}`,
			},
		})
		if (resp.status === 200)
			alert('已撤销。')
		else
			alert('撤销失败。')
	}
}

async function deleteApplication(cid) {
	if (confirm('确认删除该应用？')) {
		const vt = localStorage.verifyToken
		let resp = await fetch(`/oauth/application/${cid}`, {
			method: 'DELETE',
			headers: {
				'Authorization': `BUTKN ${vt}`,
			},
		})
		if (resp.status === 200)
			alert('已删除。')
		else
			alert('删除失败。')
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

function openAppCreatePage() {
	window.open('/oauth/application/new', '_blank')
}

async function init() {
	document.getElementById('navigator').onclick = (e) => switchOption(e)
	await setUserInfo()
	await fetchAppInfo()
}

init()
