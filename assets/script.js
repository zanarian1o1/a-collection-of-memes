document.addEventListener('DOMContentLoaded', function () {
    const mediaFolder = 'media/';
    const mediaListElement = document.querySelector('.media-list');
    const modal = document.getElementById('mediaModal');
    const closeModalButton = document.getElementById('closeModal');
    const mediaContent = document.getElementById('mediaContent');

    // Function to display images and videos
    function displayMedia(media) {
        const mediaItem = document.createElement('div');
        mediaItem.classList.add('media-item');

        if (media.endsWith('.jpg') || media.endsWith('.png') || media.endsWith('.jpeg')) {
            // For images
            const img = document.createElement('img');
            img.src = `${mediaFolder}${media}`;
            img.alt = media;
            mediaItem.appendChild(img);
        } else if (media.endsWith('.mp4') || media.endsWith('.avi') || media.endsWith('.mov')) {
            // For videos
            const video = document.createElement('video');
            video.src = `${mediaFolder}${media}`;
            video.controls = true;
            mediaItem.appendChild(video);
        }

        // Add click event to show media in modal
        mediaItem.addEventListener('click', () => showModal(media));

        mediaListElement.appendChild(mediaItem);
    }

    // Function to show modal with media content
    function showModal(media) {
        if (media.endsWith('.jpg') || media.endsWith('.png') || media.endsWith('.jpeg')) {
            mediaContent.innerHTML = `<img src="media/${media}" alt="${media}" class="modal-content">`;
        } else if (media.endsWith('.mp4') || media.endsWith('.avi') || media.endsWith('.mov')) {
            mediaContent.innerHTML = `<video src="media/${media}" class="modal-content" controls></video>`;
        }
        modal.style.display = 'flex';
    }

    // Close modal
    closeModalButton.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    // Fetch the files in the media folder using GitHub API
    const repoOwner = 'your-username'; // replace with your GitHub username
    const repoName = 'your-repo'; // replace with your repository name
    const apiUrl = `https://api.github.com/repos/${repoOwner}/${repoName}/contents/media`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                data.forEach(item => {
                    if (item.type === 'file') {
                        displayMedia(item.name);
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error fetching media files:', error);
        });
});
