'use strict'

async function parseUserAgent() {
	const parser = new UAParser(navigator.userAgent)
	const result = parser.getResult();
	let browserName = result.browser.name
	let browserVer = result.browser.version
	let osName = result.os.name
	let osVer = result.os.version
	let deviceVendor = result.device.vendor
	let deviceModel = result.device.model

	// detect Windows 10/11
	if (osName === 'Windows' && osVer === '10') {
		if (navigator.userAgentData === undefined) {
			// unable to determine
			osVer = '10/11'
		}
		else {
			const platformInfo = await navigator.userAgentData.getHighEntropyValues(["platformVersion"])
			if (navigator.userAgentData.platform === "Windows") {
				const majorPlatformVersion = parseInt(platformInfo.platformVersion.split('.')[0]);
				if (majorPlatformVersion >= 13) {
					osVer = '11'
				}
			}
		}
	}

	const browserInfo = browserVer === undefined ? browserName : `${browserName} ${browserVer}`
	const osInfo = osVer === undefined ? osName : `${osName} ${osVer}`
	let parsedResult = `${browserInfo}, ${osInfo}`
	if (deviceVendor !== undefined && deviceModel !== undefined)
		parsedResult += `, ${deviceVendor} ${deviceModel}`

	return parsedResult
}

function isMobile() {
	return (/Mobile/.test(navigator.userAgent))
}
