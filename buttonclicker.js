var button = document.getElementsByClassName("af18dbd5a4")

button.addEventListener("click", function(){
    var ws = new WebSocket("ws://localhost:4321")
    ws.onopen = function() {
        ws.send("fetch_url");
    }
})