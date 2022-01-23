<?php
session_start();

if (isset($_SESSION['user'])) {
	http_response_code(200);
	header('Content-Type: application/json');
	echo json_encode($_SESSION['user']);
}
else {
	http_response_code(403);
}