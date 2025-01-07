

function postToken(url, token) {
  return post(url, token)
}

window.post = function(url, token) {
  data = {token:token}
  return fetch(url, {method: "POST", headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
};
