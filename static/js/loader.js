window.addEventListener("load", function () {
    const loader = document.getElementById("loader");

    loader.style.opacity = "0";

    setTimeout(() => {
        loader.style.display = "none";
        document.body.style.visibility = "visible";
    }, 400);
});