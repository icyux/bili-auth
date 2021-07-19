<?php
session_start();
require_once 'bili_verify.php';

if($_SERVER['REQUEST_METHOD']==='POST' && $_GET['action']==='create'){
	$code = verifyCreate();
	$_SESSION['code'] = $code;
	echo $code;
	die;
}
if($_SERVER['REQUEST_METHOD']==='GET' && $_GET['action']==='check'){
	$result = verifyQuery($_GET['code']);
	if($result===null){
		http_response_code(404);
		die;
	}
	if($result['isAuthed']===false){
		http_response_code(403);
		die;
	}
	$_SESSION['data'] = $result;
	header('Content-Type: application/json');
	echo json_encode($result);
	die;
}

http_response_code(400);