document.addEventListener("DOMContentLoaded", function () {

  const messages = document.querySelectorAll(".message-alert");

  messages.forEach(function (msg) {
    setTimeout(function () {
      msg.style.transition =
        "opacity 0.6s ease, margin 0.6s ease, padding 0.6s ease";
      msg.style.opacity = "0";
      msg.style.margin = "0";
      msg.style.padding = "0";
      msg.style.height = "0";

      setTimeout(function () {
        msg.remove();
      }, 300);
    }, 10000);
  });
});
