const imageContainer = document.getElementById('image-container');

function loadImages() {
  fetch('/get_images')
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((images) => {
      imageContainer.innerHTML = ''; // Clear existing images
      images.forEach((image) => {
        const imgElement = document.createElement('img');
        imgElement.src = 'screenshots/' + image;
        imgElement.alt = image;
        imageContainer.appendChild(imgElement);
      });
    })
    .catch((error) => {
      console.error('Error loading images:', error);
    });
}

// Load images on page load
loadImages();

// Automatically refresh images every 5 seconds (adjust as needed)
setInterval(loadImages, 5000);
