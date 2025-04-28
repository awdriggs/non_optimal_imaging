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

            const link = document.createElement("a");
            link.href = `captures/${filename}`;
            // link.target = "_blank";  // Open in a new tab
            link.appendChild(img);

            gallery.appendChild(link);
        }
    } catch (error) {
        console.error("Failed to load images:", error);
    }
}

// Run it!
loadImages();
setInterval(loadImages, 10000);

