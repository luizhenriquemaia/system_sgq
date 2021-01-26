function menuSandwich(e) {
  var contentHidden = document.getElementById("content-for-hidden");
  var contentMenu = document.getElementById("content-menu");
  e.classList.toggle("change");
  contentHidden.classList.toggle("change");
  contentMenu.classList.toggle("change");
}


function confirmacaoDeletar(e) {
  var popupText = document.getElementsByClassName("popup-text");
  var popupButtonSim = document.getElementsByClassName("popup-button-sim");
  var popupButtonNao = document.getElementsByClassName("popup-button-nao");
  e.classList.toggle("show");
  if (popupText[0].classList.contains("show")){
    popupText[0].classList.remove("show");
    popupButtonSim[0].classList.remove("show");
    popupButtonNao[0].classList.remove("show");
  }
  else{
    popupText[0].className += " show";
    popupButtonSim[0].className += " show";
    popupButtonNao[0].className += " show";
  }
}
