console.log("Querying /api/search");
async function search(prompt) {
  let results = document.getElementById("results");
  results.innerHTML = "";

  const response = await fetch("/api/search", {
    method: 'POST',
    headers: {
      'Content-Type': 'text/plain'
    },
    body: prompt
  });
  let resp = await response.json();
  for (let path in resp.docs) {
    let item = document.createElement("span");
    item.appendChild(document.createTextNode(resp.docs[path]));
    item.appendChild(document.createElement("br"));
    results.appendChild(item);
  }
}

let query = document.getElementById("query");

query.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    search(query.value)
  }
})