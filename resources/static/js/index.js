window.addEventListener("load", function () {
  const button = document.querySelector("button.link-button");
  const checkboxes = document.querySelectorAll("input[type=checkbox]");
  checkAcknowledgements(checkboxes, button);
});
