// script.js

async function loadImages() {
    try {
        const response = await fetch(".");
        const text = await response.text();

        // Find all image links
        const imageFilenames = [...text.matchAll(/href="captures\/(.*?\.(jpg|jpeg|png))"/gi)].map(m => m[1]);

        const gallery = document.getElementById("gallery");
        gallery.innerHTML = "";

        // Sort newest first
        imageFilenames.sort().reverse();

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

