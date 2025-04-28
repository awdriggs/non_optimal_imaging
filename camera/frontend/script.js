async function loadImages() {
    try {
        const response = await fetch("/api/images");
        const imageFilenames = await response.json();

        const gallery = document.getElementById("gallery");
        gallery.innerHTML = "";

        for (const filename of imageFilenames) {
            const img = document.createElement("img");
            img.src = `captures/${filename}`;
            img.alt = filename;
            img.className = "thumbnail";
            gallery.appendChild(img);
        }
    } catch (error) {
        console.error("Failed to load images:", error);
    }
}

// Run it!
loadImages();
setInterval(loadImages, 10000);
