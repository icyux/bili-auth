'use strict'

const cid = window.location.pathname.match('/oauth/application/([^/]+)/.*')[1]
const headers = {
	'Authorization': `BUTKN ${localStorage.verifyToken}`,
}

async function updateAppInfo() {
	document.getElementById('submit-appinfo').disabled = true
	const name = document.getElementById('name').value
	const icon = document.getElementById('icon').files[0]
	const desc = document.getElementById('description').value
	const link = document.getElementById('link').value
	const prefix = document.getElementById('callback-prefix').value

	const oauthAppForm = new FormData()
	oauthAppForm.append('name', name)
	oauthAppForm.append('desc', desc)
	oauthAppForm.append('link', link)
	oauthAppForm.append('prefix', prefix)
	if (icon !== undefined)
		oauthAppForm.append('icon', icon)

	let resp = await fetch(`/oauth/application/${cid}`, {
		method: 'PUT',
		headers,
		body: oauthAppForm,
	})

	if (resp.status === 200) {
		alert('修改成功。')
		document.getElementById('submit-appinfo').disabled = false
	}
	else {
		alert('提交应用信息失败。')
		document.getElementById('submit-appinfo').disabled = false
	}
}

async function updateAppIcon() {
	if (confirm('确认更新图标？该更改将立即生效。')) {
		const icon = document.getElementById('icon').files[0]
		const formData = new FormData()
		formData.append('icon', icon)

		const resp = await fetch(`/oauth/application/${cid}/icon`, {
			method: 'PUT',
			headers,
			body: formData,
		})
		if (resp.ok) {
			const iconDisp = document.getElementById('icon-display')
			const iconSrc = iconDisp.src
			iconDisp.src = `${iconSrc}?t=${Date.now()}`
		}
		else
			alert('更新失败。')
	}
}

async function clearAppIcon() {
	if (confirm('确认清除图标？该更改将立即生效，应用图标将变为默认。')) {
		const resp = await fetch(`/oauth/application/${cid}/icon`, {
			method: 'DELETE',
			headers,
		})
		if (resp.ok) {
			const iconDisp = document.getElementById('icon-display')
			const iconSrc = iconDisp.src
			iconDisp.src = `${iconSrc}?t=${Date.now()}`
		}
		else
			alert('清除失败。')
	}
}


async function init() {
	const resp = await fetch(`/oauth/application/${cid}`, {
		headers,
	})

	if (!resp.ok) {
		alert('获取应用信息失败！')
		return
	}

	const info = await resp.json()

	document.getElementById('name').value = info['name']
	document.getElementById('description').value = info['desc']
	document.getElementById('link').value = info['link']
	document.getElementById('callback-prefix').value = info['prefix']
	document.getElementById('icon-display').src = info['icon']

	document.getElementById('loading').hidden = true
	document.getElementById('edit-app').hidden = false
}

init()
