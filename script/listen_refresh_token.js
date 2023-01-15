async function sleep(time) {
	await new Promise((resolve, reject) => setTimeout(resolve, time))
}

return await Promise.race([
	(async () => {
		const origTkn = localStorage['ac_time_value']
		while (true) {
			let curTkn = localStorage['ac_time_value']
			if (curTkn != origTkn)
				return curTkn

			await sleep(1000)
		}
	})(),
	new Promise((resolve, reject) => {
		setTimeout(() => reject('timeout'), 10000)
	}),
])
