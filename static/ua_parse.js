'use strict'

const ua = navigator.userAgent

function parseUserAgent() {

	let platform = null
	if (/Android/.test(ua))
		platform = 'Android'
	else if (/iPad/.test(ua))
		platform = 'iPad OS'
	else if (/iPhone/.test(ua))
		platform = 'iOS'
	else if (/Mac OS X/.test(ua))
		platform = 'macOS'
	else if (/Windows NT 10\.0/.test(ua))
		platform = 'Windows 10/11'
	else if (/Windows NT 6\.1/.test(ua))
		platform = 'Windows 7'
	else if (/X11; /.test(ua))
		platform = 'Linux'

	let browser = null
	if (/Firefox/.test(ua))
		browser = 'Firefox'
	else if (/MSIE/.test(ua))
		browser = 'Internet Explorer'
	else if (platform === 'Android' && /wv/.test(ua))
		browser = 'Android WebView'
	else if (/^(iPad OS|iOS|macOS)$/.test(platform) && /Safari/.test(ua))
		browser = 'Safari'
	else if (/Chrome/.test(ua))
		browser = 'Chrome'
	else if (/Chromium/.test(ua))
		browser = 'Chromium'

	return [platform, browser]
}

function isMobile() {
	return (/Mobile/.test(ua))
}
