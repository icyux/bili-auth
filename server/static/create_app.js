'use strict'

async function submitAppInfo() {
	document.getElementById('submit-appinfo').disabled = true
	const name = document.getElementById('name').value
	const icon = document.getElementById('icon-url').value
	const desc = document.getElementById('description').value
	const link = document.getElementById('link').value
	const prefix = document.getElementById('callback-prefix').value

	const vt = localStorage.verifyToken

	let resp = await fetch('/oauth/application',{
		method: 'POST',
		headers: {
			'Authorization': `BUTKN ${vt}`,
		},
		body: new URLSearchParams({
			'name': name,
			'icon': icon,
			'desc': desc,
			'link': link,
			'prefix': prefix,
		}),
	})

	if (resp.status === 200) {
		const data = await resp.json()
		document.getElementById('client-id').innerText = data['cid']
		document.getElementById('client-secret').innerText = data['csec']
		document.getElementById('create-app').hidden = true
		document.getElementById('display-info').hidden = false
	}
	else {
		alert('提交应用信息失败。')
		document.getElementById('submit-appinfo').disabled = false
	}
}
