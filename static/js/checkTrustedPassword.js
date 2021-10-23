function loginSuccess() {
    toastr.success("Redirecting you to the dashboard")
    window.location.href = "/trusted_user_dashboard"
  }
  
  $("#login").submit(function () {
    $("#button").prop("disabled", true)
    $("#img").show()
    event.preventDefault()
    $.ajax({
      url: "/checkTrustedPassword",
      data: $(this).serialize(),
      type: "POST",
      success: function (response) {
        $("#img").hide()
        if (response === "correct") {
          setTimeout(loginSuccess, 5000)
          swal
            .fire({
              icon: "success",
              title: "Login Successful",
            })
            .then((result) => {
              window.location.href = "/trusted_user_dashboard"
            })
        } else if (response === "wrong") {
          swal
            .fire({
              icon: "error",
              title: "Login Error",
              text: "Incorrect Username or password",
            })
            .then((result) => {
              $("#button").removeAttr("disabled")
            })
        }
      },
      error: function (error) {
        console.log(error)
      },
    })
  })
  