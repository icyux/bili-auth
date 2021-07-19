<?php
session_start();
require_once 'bili_verify.php';
const DB_PATH = 'comments.db';

class CustomDB extends SQLite3{
	function __construct(){
		$this->open(DB_PATH);
	}
}

$db = new CustomDB();
assert($db);

function filter($input){
	return str_replace('\'','\'\'',$input);
}

if($_SERVER['REQUEST_METHOD']==='POST'){
	if(!isset($_SESSION['data'])){
		http_response_code(403);
		die('you need to auth first. ');
	}
	switch ($_GET['action']) {
		case 'create':
			$context = filter($_POST['context']);
			if(isset($context) && strlen($context)<5000 && strlen($context)>5){
				$uid = $_SESSION['data']['uid'];
				$ts = time();
				$result = $db->exec("INSERT INTO comment (sender,context,ts) VALUES ({$uid},'{$context}',{$ts})");
				if($result){
					http_response_code(200);
				}
				else{
					http_response_code(500);
				}
			}
			else{
				http_response_code(400);
				die('out of range.');
			}
			break;

		case 'delete':
			$uid = $_SESSION['data']['uid'];
			$pid = intval($_GET['pid']);
			if($pid==0){
				http_response_code(400);
			}
			else{
				$result = $db->query("SELECT 1 FROM comment WHERE pid={$pid} and sender={$uid}");
				if(!($result->fetchArray())){
					http_response_code(403);
					die('此评论不存在，或者您无权操作。');
				}
				$result = $db->exec("DELETE FROM comment WHERE pid={$pid}");
				if($result){
					http_response_code(200);
				}
				else{
					http_response_code(500);
				}
			}
			break;
		default:
			http_response_code(400);
			break;
	}
	die;
}
?>

<!DOCTYPE html>
<head>
	<meta charset="UTF-8"/>
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
	<title>bili登录 demo</title>
</head>
<html>
	<?php if(isset($_SESSION['data'])): ?>
		<h5>您当前登录身份：</h5>
		<!-- 若有神人能解决B站头像和用户信息api跨域访问问题，不胜感激。用服务器作代理太耗带宽 -->
		<!-- 为什么不能跨域！！！你*的B...站。含泪注释 <img referrer="no-referrer" src="<?php echo $_SESSION['data']['avatar']; ?> "> -->
		<h5><?php echo $_SESSION['data']['nickname'].' (uid:'.strval($_SESSION['data']['uid']).')'; ?></h5>
		<p>个性签名: <?php echo $_SESSION['data']['bio']; ?></p>
	<?php else: ?>
		<h6>未登录。点击<a href='auth.php'>验证您的哔哩哔哩账号</a>。</h6>
	<?php endif; ?>
	<?php
		if(isset($_GET['page'])){
			$page = intval($_GET['page']);
			$index = $page*10;
		}
		else{
			$page = 0;
			$index = 0;
		}
		assert($index>=0);
		$result = $db->query("SELECT pid,sender,context,ts FROM comment ORDER BY pid DESC LIMIT {$index},10");
	?>
	<textarea onfocus='onTextareaFocus();' id='edit-comment' rows="3" cols="20">发一条友善的评论吧！</textarea>
	<input onclick='submitComment();' type='submit'>
	<p>Tip: 提交之后可以删除，随便写点什么吧。</p>
	<hr/>
	<?php while($c = $result->fetchArray(SQLITE3_ASSOC)): ?>
		<div class='comment'>
			<div id='uid' hidden><?php echo $c['sender']; ?></div>
			<!-- <img href=""> -->
			<a target='_blank'><h4 style='color:blue' id='nickname'></h4></a>
			<p id='bio' style='color:gray'></p>
			<p id='context'><?php echo $c['context']; ?></p>
			<p id='time'><?php echo $c['ts']; ?></p>
			<input type='submit' value='删除' onclick='if(confirm("确定删除？该评论将会丢失（很长时间！）")) deleteComment(<?php echo $c['pid']; ?>);'>
		</div>
		<hr/>
	<?php endwhile; ?>
	<a href='?page=<?php echo $page-1; ?>'>上一页</a>
	<div>当前第<?php echo $page; ?>页（起始页为0，每页10条）</div>
	<a href='?page=<?php echo $page+1; ?>'>下一页</a>
	<script type="text/javascript">
		var selfUid = <?php echo isset($_SESSION['data']['uid'])?$_SESSION['data']['uid']:'null'; ?>;
		var isFirstFocus = true;
		var comments = document.getElementsByClassName('comment');	
		var xhr = new XMLHttpRequest();
		for(var index = 0; index<comments.length; index++){
			let c = comments[index];
			console.log(c);
			let uid = Number(c.children[0].innerText);
			xhr.open('get',`userinfo.php?uid=${uid}`,false);
			xhr.send();
			if(xhr.status!==200){
				var name = '用户信息加载失败';
			}
			else{
				let info = JSON.parse(xhr.responseText)['data'];
				if(!info){
					var name = '用户信息加载失败';
					var time = ts2dateTime(Number(c.children[4].innerText));
				}
				else{
					var name = info['name'];
					var bio = info['sign'];
					var time = ts2dateTime(Number(c.children[4].innerText));
				}
			}
			c.children[1].href = `https://space.bilibili.com/${uid}`
			c.children[1].children[0].innerText = name;
			c.children[2].innerText = bio;
			c.children[4].innerText = time;
			c.children[5].hidden = (selfUid!==uid);
		}

		function onTextareaFocus(){
			if(isFirstFocus){
				document.querySelector("#edit-comment").innerText = '';
				isFirstFocus = false;
			}
		}

		function submitComment(){
			let comment = document.querySelector("#edit-comment").value;
			if(isFirstFocus||comment.length<5){
				alert('内容太少了');
				return false;
			}
			xhr.open('post','demo.php?action=create',false);
			xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
			xhr.send('context='+encodeURIComponent(comment));
			if(xhr.status===200){
				alert('发送成功。');
				location.reload();
			}
			else{
				alert('发送失败，等下再试试。也有可能字数太多。');
			}
		}

		function deleteComment(pid){
			xhr.open('post',`demo.php?action=delete&pid=${pid}`,false);
			xhr.send();
			if(xhr.status===200){
				alert('删除成功，刷新后消失。')
			}
			else{
				alert('删除失败，控制台可见响应错误信息。')
			}
		}

		function ts2dateTime(ts){
			var date = new Date(ts*1000);
			var Y = date.getFullYear() + '/';
			var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '/';
			var D = (date.getDate() < 10 ? '0'+date.getDate() : date.getDate()) + ' ';
			var h = date.getHours() + ':';
			var m = (date.getMinutes() < 10 ? '0'+date.getMinutes() : date.getMinutes())+ ':';
			var s = (date.getSeconds() < 10 ? '0'+date.getSeconds() : date.getSeconds());
			return Y+M+D+h+m+s;
	}
	</script>
</html>