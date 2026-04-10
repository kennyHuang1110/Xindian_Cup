(function () {
  var storageKey = 'xindianCupLineAccess';
  var protectedPaths = ['/', '/public/teams/', '/schedule/', '/history/photos/', '/charter/'];
  var path = window.location.pathname;

  function isProtectedPath(currentPath) {
    return protectedPaths.indexOf(currentPath) !== -1;
  }

  if (isProtectedPath(path) && !localStorage.getItem(storageKey)) {
    window.location.replace('/line/login/');
    return;
  }

  var loginForm = document.querySelector('[data-static-line-login]');
  if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var input = loginForm.querySelector('input[name="line_user_id"]');
      var lineUserId = input ? input.value.trim() : '';
      if (!lineUserId) {
        return;
      }
      localStorage.setItem(storageKey, lineUserId);
      window.location.href = '/';
    });
  }

  var logoutButtons = document.querySelectorAll('[data-static-line-logout]');
  logoutButtons.forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      localStorage.removeItem(storageKey);
      window.location.href = '/line/login/';
    });
  });
})();
