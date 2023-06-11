<?php
session_start();

if (isset($_SESSION['user'])) {
	http_response_code(200);
	header('Content-Type: application/json');
	$raw = $_SESSION['user'];
	$info = [
		'uid' => $raw['uid'],
		'name' => $raw['nickname'],
		'bio' => $raw['bio'],
		'avatar' => $raw['avatar'],
	];
	echo json_encode($info);
}
else {
	http_response_code(403);
}
