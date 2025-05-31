let eyeIcon = document.getElementById('eye-icon')
let password = document.getElementById('password')

eyeIcon.onclick = function () {
  if (password.type == 'password') {
    password.type = 'text'

    eyeIcon.src = '../img/eye-show.png'
  } else {
    password.type = 'password'

    eyeIcon.src = '../img/eye-close.png'
  }
}

modal = getElementById('modal')
closeButton = getElementById('close-modal-btn')


// load pop on page load
const modal = document.getElementById("modal");
const closeButton = document.getElementById("close-modal-btn");
const btn = document.getElementsByName("button");

document.addEventListener("DOMContentLoaded", function (e) {
  modal.classList.remove("hidden");
  console.log("modal output");
});
closeButton.addEventListener('click', function (e) {
  modal.classList.add('hidden')
})
