window.onload = function() {
    const M = window.M;
    var elems = document.querySelectorAll('.tooltipped');
    var instances = M.Tooltip.init(elems);
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems);
    M.updateTextFields();
}