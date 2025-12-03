document.addEventListener('DOMContentLoaded', () => {
    // 1. Get the current card and button elements
    const card = document.getElementById('swipe-card');
    const likeBtn = document.getElementById('like-btn');
    const dislikeBtn = document.getElementById('dislike-btn');

    // --- State Variables ---
    let startX = 0;
    let offsetX = 0;
    let isSwiping = false;
    const SWIPE_THRESHOLD = 100; // Pixels needed to trigger a complete swipe

    if (!card) return; // Exit if no card is present

    // Function to handle the swipe action (communicate with backend)
    const handleSwipeAction = (direction) => {
        // We use the ID to identify the user currently on the card
        const userId = card.getAttribute('data-user-id'); 
        
        // 🎯 AJAX Request to Python Backend (e.g., /swipe)
        fetch('/swipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // If you use Flask/Django sessions, you might need a CSRF token here
            },
            body: JSON.stringify({ 
                user_id: userId, 
                action: direction // 'like' or 'dislike'
            })
        })
        .then(response => {
            // Check for a success status before parsing JSON
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Swipe Successful:', data);
            
            // Remove the card from the DOM after successful backend processing
            card.remove(); 
            
            // 💡 Simplest way to load the next card is reloading the page.
            // A better way is to use JavaScript to fetch and insert the next card's HTML.
            window.location.reload(); 
        })
        .catch(error => {
            console.error('Error during swipe:', error);
            // If the swipe fails, reset the card's position
            resetCard();
            alert('Failed to process swipe. Please try again.');
        });
    };

    // Function to reset the card position and style
    const resetCard = () => {
        // Remove animation classes and reset the card to the center
        card.classList.remove('swipe-left-anim', 'swipe-right-anim');
        card.style.transition = 'transform 0.3s cubic-bezier(.68,-0.55,.27,1.55)'; // Fun bounce transition
        card.style.transform = 'translate(0px, 0px) rotate(0deg)';
        card.style.opacity = '1';
        offsetX = 0;
    };

    // --- Drag Handlers (Mousedown/Touchstart) ---
    const startDrag = (e) => {
        e.preventDefault();
        isSwiping = true;
        // Check for touch event or mouse event
        startX = e.clientX || e.touches[0].clientX;
        card.style.transition = 'none'; // Disable transition during drag for smooth movement
    };

    // --- Drag Handlers (Mousemove/Touchmove) ---
    const onDrag = (e) => {
        if (!isSwiping) return;

        const currentX = e.clientX || e.touches[0].clientX;
        offsetX = currentX - startX;

        // Calculate rotation based on drag distance
        const rotation = offsetX / 25; // 25 is a sensitivity value
        const maxRotation = Math.min(Math.max(rotation, -15), 15);

        // Apply visual transformation
        card.style.transform = `translate(${offsetX}px, 0px) rotate(${maxRotation}deg)`;
    };

    // --- Drag Handlers (Mouseup/Touchend) ---
    const endDrag = () => {
        if (!isSwiping) return;
        isSwiping = false;
        
        // Determine if a swipe threshold was met
        if (offsetX > SWIPE_THRESHOLD) {
            // Swiped Right (LIKE) - Apply animation class
            card.classList.add('swipe-right-anim'); 
            setTimeout(() => handleSwipeAction('like'), 500); // Wait for animation before backend call
        } else if (offsetX < -SWIPE_THRESHOLD) {
            // Swiped Left (DISLIKE) - Apply animation class
            card.classList.add('swipe-left-anim');
            setTimeout(() => handleSwipeAction('dislike'), 500); // Wait for animation before backend call
        } else {
            // Failed to swipe, reset the card
            resetCard();
        }
    };

    // --- Button Click Handlers ---
    if (likeBtn) {
        likeBtn.addEventListener('click', () => {
            card.classList.add('swipe-right-anim'); // Use the CSS class for animation
            setTimeout(() => handleSwipeAction('like'), 500);
        });
    }

    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', () => {
            card.classList.add('swipe-left-anim'); // Use the CSS class for animation
            setTimeout(() => handleSwipeAction('dislike'), 500);
        });
    }

    // --- Attach Event Listeners ---
    card.addEventListener('mousedown', startDrag);
    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', endDrag);

    // --- Attach Touch Event Listeners for mobile ---
    card.addEventListener('touchstart', startDrag);
    document.addEventListener('touchmove', onDrag);
    document.addEventListener('touchend', endDrag);
});
