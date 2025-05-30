document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const newsContainer = document.getElementById('news-container');
    const newsDetails = document.getElementById('news-details');
    const commentForm = document.getElementById('comment-form');
    const commentsList = document.getElementById('comments-list');
  
const fetchNews = async () => {
    try {
        const response = await fetch('/news/get', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const newsList = await response.json();
            newsContainer.innerHTML = ''; // Clear the container

            newsList.forEach((news, index) => {
                const publishedAt = news.published_at ? new Date(news.published_at) : null;
                const lastUpdated = news.last_updated ? new Date(news.last_updated) : null;

                const formattedPublishedAt = publishedAt && !isNaN(publishedAt) 
                    ? publishedAt.toLocaleDateString() 
                    : "Unknown Date";
                
                const formattedLastUpdated = lastUpdated && !isNaN(lastUpdated) 
                    ? lastUpdated.toLocaleDateString() 
                    : "Not Updated";

                // Create news item
                const newsItem = document.createElement('div');
                newsItem.className = 'news-item';
                newsItem.innerHTML = `
                    <h3>${news.title}</h3>
                    <p>${news.content.substring(0, 100)}...</p>
                    <p><strong>Author:</strong> ${news.author}</p>
                    <p><strong>Published At:</strong> ${formattedPublishedAt}</p>
                    <p><strong>Last Updated:</strong> ${formattedLastUpdated}</p>
                    <button data-id="${news.news_id}" class="view-details">View Details</button> 
                `;

                newsContainer.appendChild(newsItem);

                // Add a separator after each news item except the last one
                if (index < newsList.length - 1) {
                    const separator = document.createElement('hr');
                    separator.className = 'news-separator';
                    newsContainer.appendChild(separator);
                }
            });

            // Add event listeners to "View Details" buttons
            document.querySelectorAll('.view-details').forEach((button) =>
                button.addEventListener('click', () => fetchNewsDetails(button.dataset.id))
            );
        } else {
            newsContainer.innerHTML = '<p>Failed to load news articles.</p>';
        }
    } catch (error) {
        console.error('Error fetching news:', error);
        newsContainer.innerHTML = '<p>An error occurred while loading news articles.</p>';
    }
};
/**************************************************************************************************************/
// Read Endpoint {/news/get/{newsId)}
// Fetch and display a single news article

const fetchNewsDetails = async (newsId) => {
    try {
        const response = await fetch(`/news/get/${newsId}`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const news = await response.json();

            // Handle potential missing dates
            const publishedAt = news.published_at ? new Date(news.published_at) : null;
            const lastUpdated = news.last_updated ? new Date(news.last_updated) : null;

            const formattedPublishedAt = publishedAt && !isNaN(publishedAt)
                ? publishedAt.toLocaleDateString()
                : "Unknown Date";

            const formattedLastUpdated = lastUpdated && !isNaN(lastUpdated)
                ? lastUpdated.toLocaleDateString()
                : "Not Updated";

            // Populate news details
            document.getElementById('news-title').textContent = news.title;
            document.getElementById('news-content').textContent = news.content;
            document.getElementById('news-author').textContent = news.author;
            document.getElementById('news-published-at').textContent = formattedPublishedAt;
            document.getElementById('news-last-updated').textContent = formattedLastUpdated;

            // Display comments
            commentsList.innerHTML = '';
            news.comments.forEach((comment) => {
                const commentItem = document.createElement('li');
                const commentDate = comment.date ? new Date(comment.date).toLocaleString() : "Unknown Time";
                commentItem.textContent = `${comment.username}: ${comment.content} (${commentDate})`;
                commentsList.appendChild(commentItem);
            });

            // Add "Back" button to return to all news
            const backButton = document.createElement('button');
            backButton.textContent = "Back to News";
            backButton.className = "back-button";
            backButton.addEventListener('click', () => {
                document.getElementById('news-list').style.display = 'block';
                document.getElementById('news-details').style.display = 'none';
            });

            // Clear previous button before appending a new one
            const buttonContainer = document.getElementById('back-button-container');
            buttonContainer.innerHTML = ''; // Prevent duplicate buttons
            buttonContainer.appendChild(backButton);

            // Show news details and hide the list
            document.getElementById('news-list').style.display = 'none';
            document.getElementById('news-details').style.display = 'block';

/**************************************************************************************************************/
// Read Endpoint {/news/comment/{news_id}}}

// Attach comment submission handler


    commentForm.onsubmit = async (event) => {
        event.preventDefault();
        const commentContent = document.getElementById('comment-content').value;

        try {
        const commentResponse = await fetch(`/news/comment/${newsId}`, {
            method: 'PUT',
            headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ comment_content: commentContent }),
        });

        if (commentResponse.ok) {
            // Refresh comments
            fetchNewsDetails(newsId);
            commentForm.reset(); // Clear the comment form
        } else {
            alert('Failed to add comment.');
        }
        } catch (error) {
        console.error('Error adding comment:', error);
        }
    };
    } else {
    alert('Failed to load news details.');
    }
} catch (error) {
    console.error('Error fetching news details:', error);
}
};


/****************************************************************************************************************/
// Initialize the page
fetchNews();
});