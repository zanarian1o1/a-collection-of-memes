document.addEventListener('DOMContentLoaded', () => {
    const MEDIA_FOLDER = 'media/';
    const API_URL = 'https://api.github.com/repos/zanarian1o1/a-collection-of-memes/contents/media';

    const mediaListElement = document.querySelector('.media-list');
    const modal = document.getElementById('mediaModal');
    const closeModalButton = document.getElementById('closeModal');
    const mediaContent = document.getElementById('mediaContent');

    /**
     * Displays an individual media item (image or video) in the list.
     * @param {string} media - The name of the media file.
     */
    function displayMedia(media) {
        const mediaItem = document.createElement('div');
        mediaItem.classList.add('media-item');

        if (isImage(media)) {
            const img = document.createElement('img');
            img.src = `${MEDIA_FOLDER}${media}`;
            img.alt = media;
            mediaItem.appendChild(img);
        } else if (isVideo(media)) {
            const video = document.createElement('video');
            video.src = `${MEDIA_FOLDER}${media}`;
            video.controls = true;
            video.style.objectFit = 'contain'; // Ensure proper scaling by default
            mediaItem.appendChild(video);
        }

        mediaItem.addEventListener('click', () => showModal(media));
        mediaListElement.appendChild(mediaItem);
    }

    /**
     * Checks if a file is an image based on its extension.
     * @param {string} fileName - The file name to check.
     * @returns {boolean} - True if the file is an image.
     */
    function isImage(fileName) {
        return /\.(jpg|jpeg|png)$/i.test(fileName);
    }

    /**
     * Checks if a file is a video based on its extension.
     * @param {string} fileName - The file name to check.
     * @returns {boolean} - True if the file is a video.
     */
    function isVideo(fileName) {
        return /\.(mp4|avi|mov)$/i.test(fileName);
    }

    /**
     * Displays the media in a modal.
     * @param {string} media - The name of the media file.
     */
    function showModal(media) {
        mediaContent.innerHTML = '';

        if (isImage(media)) {
            const img = document.createElement('img');
            img.src = `${MEDIA_FOLDER}${media}`;
            img.alt = media;
            img.classList.add('modal-content');
            mediaContent.appendChild(img);
        } else if (isVideo(media)) {
            const video = document.createElement('video');
            video.src = `${MEDIA_FOLDER}${media}`;
            video.controls = true;
            video.classList.add('modal-content');
            video.style.objectFit = 'contain'; // Prevent clipping in fullscreen

            video.addEventListener('fullscreenchange', () => {
                if (document.fullscreenElement) {
                    video.style.objectFit = 'contain';
                } else {
                    video.style.objectFit = 'contain';
                }
            });

            mediaContent.appendChild(video);
        }

        modal.style.display = 'flex';
    }

    /**
     * Closes the modal.
     */
    function closeModal() {
        modal.style.display = 'none';
    }

    closeModalButton.addEventListener('click', closeModal);

    /**
     * Fetches the list of media files from the GitHub API and displays them.
     */
    function fetchMedia() {
        fetch(API_URL)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (Array.isArray(data)) {
                    data.filter(item => item.type === 'file').forEach(item => displayMedia(item.name));
                }
            })
            .catch(error => {
                console.error('Error fetching media files:', error);
            });
    }

    fetchMedia();
});
