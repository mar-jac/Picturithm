<?php

if(isset($_POST["token"])){
    $token = $_POST["token"];
    echo file_get_contents("images/".$token.".status");
}

?>