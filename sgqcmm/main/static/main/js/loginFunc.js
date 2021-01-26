var butLogin = document.getElementById("butLogin");
var butEntrar = document.getElementById("butEntrar");
var form = document.getElementById("formEntrar");
var formSpace = document.getElementsByClassName("formSpace");
var inputs = document.getElementsByTagName("input");
var imgLogo = document.getElementsByClassName("imgLogo");

butLogin.onclick = function(){
  butLogin.style.visibility = "hidden";
  butLogin.style.width = 0;
  butLogin.style.height = 0;
  imgLogo[0].className = "imgLogoExtends";
  butEntrar.style.visibility = "visible";
  form.style.visibility = "visible";
  form.style.position = "relative"
  formSpace[0].className = "formSpaceExpanded";
  inputs[1].className = "inputLogin";
  inputs[2].className = "inputLogin";
};
