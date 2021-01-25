<?php


$ext = "";
$token = bin2hex(random_bytes(32));

if (isset($_POST["type"])) {
    if ($_POST["type"] == "url") {
        if (isset($_POST["url"])) {
            $file = file_get_contents($_POST["url"]);
            if ($file === FALSE) {
                http_response_code(400);
                die();
            }
            else{
                $parts = explode(".", $_POST["url"]);
                if(count($parts)>1)
                {
                    $ext = $parts[count($parts) - 1];
                    if ($ext == "gif") {
                        copy($_POST["url"], "images/$token.gif");
                    }
                }
            }
        }
    } else if ($_POST["type"] == "file") {
        if (isset($_FILES["file"])) {
            $file = file_get_contents($_FILES["file"]["tmp_name"]);
            $ext = explode("/", $_FILES["file"]["type"])[1];
            if ($ext == "gif") {
                move_uploaded_file($_FILES["file"]["tmp_name"], "images/$token.gif");
            }
        } else {
            http_response_code(400);
            die();
        }
    } else {
        http_response_code(400);
        die();
    }
} else {
    http_response_code(400);
    die();
}
$tilesx = 10;
$tilesy = 10;
if (isset($_POST["tilesx"])) {
    $tilesx = $_POST["tilesx"];
}
if (isset($_POST["tilesy"])) {
    $tilesy = $_POST["tilesy"];
}
$img = imagecreatefromstring($file);

$length = min(imagesx($img), imagesy($img));
$img3 = $img;
//$imgfail = TRUE;

if ($img3 !== FALSE) {
    $imgfail = FALSE;
    imagepng($img3, 'images/' . $token);
}

imagedestroy($img);

if ($imgfail) {
    http_response_code(400);
    die();
}

file_put_contents("images/" . $token . ".status", "0");

pclose(popen("START /B python export_5.py images/" . $token . " output/" . $token . ".mp4 $tilesx $tilesy", "w"));
//shell_exec("python export.py images/".$token." output/".$token.".mp4 &");

echo $token;

?>