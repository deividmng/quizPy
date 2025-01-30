function sendScore(points) {
    fetch("/save_score/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")  // Django necesita CSRF token
        },
        body: `points=${points}`
    })
    .then(response => {
        if (response.ok) {
            window.location.href = "/leaderboard/";  // Redirige a la tabla de clasificación
        }
    })
    .catch(error => console.error("Error:", error));
}

// Función para obtener el token CSRF de las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Ejemplo de cómo llamar a sendScore cuando termine una partida
document.getElementById("saveScoreBtn").addEventListener("click", function() {
    let points = document.getElementById("score").innerText; // Obtiene la puntuación del HTML
    sendScore(points);
});
