<?php session_start(); ?>
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8"/>
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
	<title>验证您的哔哩哔哩账号</title>
</head>
<body>
	<?php if(isset($_SESSION['data'])): ?>
		<p>您已经以"<?php echo $_SESSION['data']['nickname'] ?>"身份登录。</p>
	<?php else: ?>
		<div id='step-0'>
			<p>您将以发送信息至我们的机器人账号的方式完成验证。</p>
			<p>此验证足够简单，您只需要少于一分钟的时间和一个可以收发消息的哔哩哔哩账号即可。</p>
			<input onclick='create();' type="submit" name="test" value='开始验证'>
		</div>
		<div id='step-1' hidden>
			<div>发送私信"<div style='color:blue' id='msg'></div>"至哔哩哔哩用户（机器人）<a href="https://message.bilibili.com/#whisper/mid1521021206" target='_blank'>@BotFather</a>，发送后默数5秒（数慢点，别急了），然后点击"下一步"</div>
			<input onclick='verify();' type="submit" name="next" value="下一步">
		</div>
		<div id='step-2' hidden>
			<p id='result'>等待服务器返回验证结果...</p>
		</div>
	<?php endif; ?>
		<script type="text/javascript">
			var step = 0;
			var code = '';
			var data = {};
			var startBtn = document.querySelector("#step-0 > input[type=submit]");
			var nextBtn = document.querySelector("#step-1 > input[type=submit]");
			var resultToast = document.querySelector("#result");
			var msgDiv = document.querySelector("#msg");

			function create(){
				startBtn.disabled = true;
				startBtn.value = '正在提交...';
				var xhr = new XMLHttpRequest();
				xhr.open('post','api.php?action=create',false);
				xhr.send();
				if(xhr.status!==200){
					alert('请求异常，稍后重试。')
					startBtn.disabled = false;
					startBtn.value = '开始验证';
					return false;
				}
				code = xhr.responseText;
				msgDiv.innerText = `auth(${code})`;
				nextStep();
			}

			function verify(){
				nextBtn.disabled = true;
				var xhr = new XMLHttpRequest();
				xhr.open('get',`api.php?action=check&code=${code}`,false);
				xhr.send();
				if(xhr.status!==200){
					alert('未查询到您发送的信息。请在收到私信回复之后再提交验证。');
					nextBtn.disabled = false;
					return false;
				}
				nextStep();
				let data = JSON.parse(xhr.responseText);
				let userName = data['nickname'];
				let uid = data['uid'];
				let welcomeMsg = `验证完成，以"${userName}"(uid:${uid})的身份登录。点击浏览器的"后退"键即可回到主页面。`;
				resultToast.innerText = welcomeMsg;
			}

			function nextStep(){
				step++;
				for(let i=0;i<3;i++){
					document.querySelector(`#step-${i}`).hidden = i===step?false:true;
				}
			}

		</script>
</body>
</html>