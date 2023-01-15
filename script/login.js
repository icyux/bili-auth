async function sleep(time) {
	await new Promise((resolve, reject) => setTimeout(resolve, time))
}

async function toast(msg) {
	await new Promise(resolve => {
		const styleArr = [
			'position: absolute',
			'z-index: 114514',
			'width: 50vw',
			'height: 30vh',
			'top: 0',
			'margin: 35vh 20vw',
			'padding: 1.6rem',
			'background-color: #6aee',
			'color: white',
			'text-align: center',
		]
		const elm = document.createElement('div')
		elm.id = 'hoverToast'
		elm.style.cssText = styleArr.join(';\n')
		elm.innerHTML = `
			<pre style='font-size: 1.6rem'>${msg}</pre>
			<p>点击关闭提示</p>
		`
		elm.onclick = () => {
			elm.remove()
			resolve()
		}
		document.body.appendChild(elm)
	})
}

await toast('请登录您的账号。\n登录完成后，凭据会被自动保存。')

let refreshTkn
while (refreshTkn === undefined) {
	refreshTkn = localStorage['ac_time_value']
	await sleep(1000)
}

await toast('登录成功。\n凭据将保存在 credential.toml 中。')
return refreshTkn
