

function postToken(url, token) {
  return post(url, token)
};

window.post = function(url, token) {
  data = {token:token}
  return fetch(url, {method: "POST", headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
};

function copyLinkUrl(id) {


  const url = "/admin5/" + id;

  async function getData() {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const json = await response.json();
      var link = json.link

      // Copy the text inside the text field
      navigator.clipboard.writeText(link);

      // Alert the copied text
      alert("Copied the text: " + link);

    } catch (error) {
      console.error(error.message);
    }
  }

  getData()

};

function toggle_eq_view() {
  var x = document.getElementById("eq_res_disp");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}

function minTable(ele) {
  var divsToHide = document.getElementsByClassName(ele); //divsToHide is an array
  for(var i = 0; i < divsToHide.length; i++){
      divsToHide[i].classList.add("d-none")
  }
}

function maxTable(ele) {
  var divsToHide = document.getElementsByClassName(ele); //divsToHide is an array
  for(var i = 0; i < divsToHide.length; i++){
      divsToHide[i].classList.remove("d-none")
  }
}

function showGenre(item) {
  document.getElementById("dropdownMenu1").innerHTML = item.innerHTML;
}
