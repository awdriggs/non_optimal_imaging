async function loadImages() {
    try {
        const response = await fetch('/images/');
        const imageFilenames = await response.json();

        imageFilenames.reverse(); // Newest first

        const gallery = document.getElementById('gallery');
        gallery.innerHTML = '';

        if (imageFilenames.length === 0) {
            // No images found
            const noImagesText = document.createElement('h2');
            noImagesText.textContent = "No Captures Yet";
            noImagesText.style.marginTop = "50px";
            gallery.appendChild(noImagesText);
            return;
        }

        imageFilenames.forEach(filename => {
            const img = document.createElement('img');
            img.src = '/Captures/' + filename;  // IMPORTANT: Prefix with Captures
            img.alt = filename;
            img.onclick = () => window.open('/captures/' + filename, '_blank');
            gallery.appendChild(img);
        });
    } catch (err) {
        console.error('Error loading images', err);
    }
}

loadImages();
setInterval(loadImages, 10000);

