function tokenSuccess(err, response) {
    if (err) {
      throw err;
    }
    $window.sessionStorage.accessToken = response.body.access_token;
  }
