<?php


if(isset($_POST["type"])){
    if($_POST["type"] == "url"){
        if(isset($_POST["url"])){
            $file = file_get_contents($_POST["url"]);
            if($file === FALSE){
                http_response_code(400); die();
            }
        }
    } else if($_POST["type"] == "file"){
        if(isset($_FILES["file"])){
            $file = file_get_contents($_FILES["file"]["tmp_name"]);
        } else {
            http_response_code(400); die();
        }
    } else {
        http_response_code(400); die();
    }
} else {
    http_response_code(400); die();
}

$token = bin2hex(random_bytes(32));

$img = imagecreatefromstring($file);
$length = min(imagesx($img), imagesy($img));
$img2 = imagecrop($img, ['x' => 0, 'y' => 0, 'width' => $length, 'height' => $length]);
$img3 = imagescale($img2, 300, 300);
$imgfail = TRUE;

if($img3 !== FALSE){
    $imgfail = FALSE;
    imagepng($img3, 'images/'.$token);
} 

imagedestroy($img);
imagedestroy($img2);
imagedestroy($img3);

if($imgfail) {
    http_response_code(400); die();
}

file_put_contents("images/".$token.".status", "0");

pclose(popen("START /B python export.py images/".$token." output/".$token.".mp4", "w"));
//shell_exec("python export.py images/".$token." output/".$token.".mp4 &");

echo $token;

?>