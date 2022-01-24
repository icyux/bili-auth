<?php
session_start();

const check_max_age = 600;
const redirect = './';
const api_url = 'https://bili-auth.icyu.me:41259/oauth/access_token';
const client_id = '1a1b4514';
const client_secret = 'qgfwgwt4g';

if (isset($_GET['code']))
	$code = $_GET['code'];
else {
	http_response_code(400);
	echo 'empty code param';
	die;
}

$curl = curl_init();
curl_setopt_array($curl, [
	CURLOPT_URL => api_url.'?client_id='.client_id.'&client_secret='.client_secret.'&code='.$code,
	CURLOPT_RETURNTRANSFER => true,
	CURLOPT_ENCODING => '',
	CURLOPT_MAXREDIRS => 10,
	CURLOPT_TIMEOUT => 0,
	CURLOPT_FOLLOWLOCATION => true,
	CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
	CURLOPT_CUSTOMREQUEST => 'POST',
]);
$resp = curl_exec($curl);

if (curl_getinfo($curl, CURLINFO_HTTP_CODE) === 200) {
	http_response_code(200);
	$json = json_decode($resp, true);
	$_SESSION['user'] = $json;
	$_SESSION['user']['next_check'] = time() + check_max_age;
	header('Location: '.redirect);
}
else {
	http_response_code(400);
	echo 'Failed to fetch access_token';
}
