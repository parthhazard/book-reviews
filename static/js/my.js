function myFunc() {
  $('#form-1').toggleClass("disp-none");
  $('#form-2').toggleClass("disp-none");
  var x3 = document.getElementById('next');
  if (x3.innerHTML == "Next") {
    x3.innerHTML = "Back";
  } else {
    x3.innerHTML = "Next";
  }
  $('#next').toggleClass('float-right mt-n65');
}

function readMoreLess(x) {
  var btn = x.querySelector("#btn-more")
  var dots = x.querySelector("#dots");
  var more = x.querySelector("#more");

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    btn.innerHTML = "Read More";
    more.style.display = "none";
  } else {
    dots.style.display = "none";
    btn.innerHTML = "Read Less";
    more.style.display = "inline";
  }

}

$('.searchNav').click(function () {
  $('.searchSection').toggleClass('d-none');
});

$('tr.searchRow').click(function() {
  window.location = $(this).data("href");
});
