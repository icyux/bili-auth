'use strict';

var page = 0;
const pageCommentCount = 10;
var userDetail = {};
var avatars = {};

async function init() {
	let user;
	let comments;
	await Promise.all([
			(async () => {
				let resp = await fetch('login_status.php');
				if (resp.status !== 200) {
					document.getElementById('not-login').hidden = false;
				}
				else {
					let user = await resp.json();
					document.getElementById('self-name').innerText = user['nickname']
					document.getElementById('self-avatar').src = await fetchAvatar(user['avatar']);
					document.getElementById('self-bio').innerText = user['bio'];
					document.getElementById('user-info').hidden = false;
				}
				document.getElementById('login-pending').hidden = true;

			})(),
			(async () => {
				let resp = await fetch(`comment.php?from=${page*pageCommentCount}&count=${pageCommentCount}`);
				comments = await resp.json();
			})(),
		]);

	for (const cmt of comments) {
		if (userDetail[cmt['sender']] === undefined)
			userDetail[cmt['sender']] = null;
	}

	let tasks = [];
	for (const uid in userDetail) {
		if (userDetail[uid] === null)
			tasks.push((async () => {
					let resp = await fetch(`userinfo.php?uid=${uid}`);
					if (resp.status !== 200)
						throw new Error(`fetching user(${uid}) info failed with status: ${resp.status}`);

					let info = await resp.json();
					userDetail[uid] = info;
					await fetchAvatar(userDetail[uid]['face']);
				})());
	}
	await Promise.all(tasks);

	displayComments(comments)
}

function displayComments(comments) {
	let cmtCtn = document.getElementById('comment-container');
	cmtCtn.innerHTML = '';
	for (const cmt of comments) {
		let uid = cmt['sender'];
		let tpl = document.getElementById('cmt-template');
		tpl.content.getElementById('nickname-link').href = `https://space.bilibili.com/${uid}`;
		tpl.content.getElementById('nickname').innerText = userDetail[uid]['name'];
		tpl.content.getElementById('avatar').src = avatars[userDetail[uid]['face']];
		tpl.content.getElementById('bio').innerText = userDetail[uid]['sign'];
		tpl.content.getElementById('context').innerText = cmt['context'];
		let clone = document.importNode(tpl.content, true);
		cmtCtn.appendChild(clone);
	}
}

async function fetchAvatar(url) {
	let origin = url;
	url = url.replace('http://', 'https://');
	if (avatars[url])
		return avatars[url];

	let resp;
	try {
		resp = await fetch(`https://bili-auth.icyu.me:41259/proxy/avatar?url=${encodeURIComponent(url)}` + '@40w_40h_1c_1s.webp');
	}
	catch (e) {
		return null;
	}
	let data = await resp.blob();
	let srcURL = URL.createObjectURL(data);
	avatars[origin] = srcURL;
	return srcURL;
}

init();
