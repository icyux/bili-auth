'use strict';

const client_id = '1a1b4514';
const oauth_service = 'https://bili-auth.icyu.me:41259/oauth/authorize'
var page = 0;
const pageCommentCount = 10;
var user;
var userDetail = {};
var avatars = {};
var selfUid;

async function init() {
	let resp = await fetch('login_status.php');
	if (resp.status !== 200) {
		document.getElementById('not-login').hidden = false;
		let callback = location.origin + location.pathname +'oauth.php';
		let oauthURL = `${oauth_service}?client_id=${client_id}&redirect_uri=${encodeURIComponent(callback)}`;
		document.getElementById('oauth-service').href = oauthURL;
	}
	else {
		document.getElementById('submit-comment').disabled = false;
		document.getElementById('submit-comment').innerText = '提交';
		user = await resp.json();
		selfUid = user['uid'];
		document.getElementById('self-name').innerText = user['nickname']
		document.getElementById('self-avatar').src = await fetchAvatar(user['avatar']);
		document.getElementById('self-bio').innerText = user['bio'];
		document.getElementById('user-info').hidden = false;
	}
	document.getElementById('login-pending').hidden = true;

	await incPage(0);
}

function displayComments(comments, rmPrevCmt=true) {
	let cmtCtn = document.getElementById('comment-container');
	if (rmPrevCmt)
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
		if (uid === selfUid) {
			clone.getElementById('del').onclick = () => {
				if (confirm('确认删除评论？')) deleteComment(cmt['pid']);
			};
			clone.getElementById('del').hidden = false;
		}
		cmtCtn.appendChild(clone);
	}
}

async function fetchAvatar(url) {
	let origin = url;
	url = url.replace('http://', 'https://');
	if (avatars[origin])
		return avatars[url];

	let resp;
	try {
		resp = await fetch(`https://bili-auth.icyu.me:41259/proxy/avatar?url=${encodeURIComponent(url)}` + '@32w_32h_1c_1s.webp');
	}
	catch (e) {
		return null;
	}
	let data = await resp.blob();
	let srcURL = URL.createObjectURL(data);
	avatars[origin] = srcURL;
	return srcURL;
}

async function submitComment() {
	let content = document.getElementById('edit-comment').value;
	let resp = await fetch('comment_modify.php', {
		method: 'post',
		credentials: 'same-origin',
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
		},
		body: `content=${encodeURIComponent(content)}`,
	});
	if (resp.status == 201) {
		alert('提交成功，刷新后显示。');
	}
	else {
		throw new Error(resp);
		alert('提交失败，控制台已输出异常。');
	}
}

async function deleteComment(pid) {
	let resp = await fetch(`comment_modify.php?pid=${pid}`, {
		method: 'delete',
		credentials: 'same-origin',
	});
	if (resp.status === 200) {
		alert('删除成功，刷新后消失。');
	}
	else {
		throw new Error(resp);
		alert('删除失败，控制台已输出异常。');		
	}
}

function ts2date(ts){
	var date = new Date(ts*1000);
	var Y = date.getFullYear() + '/';
	var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '/';
	var D = (date.getDate() < 10 ? '0'+date.getDate() : date.getDate()) + ' ';
	var h = date.getHours() + ':';
	var m = (date.getMinutes() < 10 ? '0'+date.getMinutes() : date.getMinutes())+ ':';
	var s = (date.getSeconds() < 10 ? '0'+date.getSeconds() : date.getSeconds());
	return ''.concat(Y, M, D, h, m, s);
}

async function incPage(delta) {
	page += delta;

	let resp = await fetch(`comment.php?from=${page*pageCommentCount}&count=${pageCommentCount}`);
	let comments = await resp.json();
	if (comments.length === 0) {
		page -= delta;
		alert('没有评论了');
		return;
	}

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

	displayComments(comments);
	document.getElementById('page-count').innerText = page;
}

init();
