const token = localStorage.getItem("token");
let currentEditingNewsId = null;

// Load News on Page Load
document.addEventListener("DOMContentLoaded", fetchHRNews);

/***************************************************************************************************************/

// Fetch All News
async function fetchHRNews() {
    const newsList = document.getElementById("newsList");

    if (!newsList) {
        console.error("Error: Element with ID 'newsList' not found.");
        return;
    }

    try {
        const response = await fetch("/news/get", {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            console.error("Error fetching news:", response.statusText);
            return;
        }

        const newsArticles = await response.json();
        newsList.innerHTML = ''; // Clear existing news list

        newsArticles.forEach(news => {
            const li = document.createElement("li");

            li.innerHTML = `
                <h4>${news.title}</h4>
                <p>${news.content}</p>
                <small>By: ${news.author} | ${new Date(news.published_at).toLocaleDateString()}</small>

                <div class="button-container"><br>
                    <button onclick="openNewsModal('${news.news_id}', '${news.title}', '${news.content}')">Edit</button>
                    <button class="delete" onclick="openDeleteModal('${news.news_id}')">Delete</button>
                </div>
            `;

            newsList.appendChild(li);
        });

    } catch (error) {
        console.error("Error fetching news:", error);
    }
}

/***************************************************************************************************************/

// Open the Add/Edit News Modal
function openNewsModal(newsId = null, title = "", content = "") {
    const modal = document.getElementById("newsModal");
    document.getElementById("modal-title").textContent = newsId ? "Edit News" : "Add News";
    document.getElementById("modal-news-title").value = title;
    document.getElementById("modal-news-content").value = content;
    modal.style.display = "block";

    currentEditingNewsId = newsId; // Store current news ID for editing

    // Handle cancel button
    document.getElementById("closeModal").onclick = () => {
        modal.style.display = "none"; // Close modal without saving
    };

    // Handle saving news
    document.getElementById("saveNews").onclick = async () => {
        if (newsId) {
            await updateNews(newsId);
        } else {
            await addNews();
        }
        modal.style.display = "none"; // Close modal after saving
    };
}

// Add News Function
async function addNews() {
    const title = document.getElementById("modal-news-title").value.trim();
    const content = document.getElementById("modal-news-content").value.trim();

    if (!title || !content) {
        showModal("Title and Content cannot be empty", "failure");
        return;
    }

    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);

    try {
        const response = await fetch("/news/hr/create", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: formData
        });

        if (response.ok) {
            showModal("News Added Successfully", "success");
            fetchHRNews();
        } else {
            showModal("Failed to Add News", "failure");
        }
    } catch (error) {
        console.error("Error adding news:", error);
        showModal("An error occurred while adding news.", "failure");
    }
}

// Edit News Function
async function updateNews(newsId) {
    const title = document.getElementById("modal-news-title").value.trim();
    const content = document.getElementById("modal-news-content").value.trim();

    if (!title || !content) return;

    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);

    try {
        const response = await fetch(`/news/hr/edit/${newsId}`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${token}` },
            body: formData
        });

        if (response.ok) {
            showModal("News Updated", "success");
            fetchHRNews();
        } else {
            showModal("Failed to Update News", "failure");
        }
    } catch (error) {
        console.error("Error updating news:", error);
    }
}

/***************************************************************************************************************/

// Open Delete Confirmation Modal
function openDeleteModal(newsId) {
    const modal = document.getElementById("deleteModal");
    modal.style.display = "block";

    // Handle confirm delete
    document.getElementById("confirmDelete").onclick = async () => {
        await deleteNews(newsId);
        modal.style.display = "none"; // Close modal after deleting
    };

    // Handle cancel button
    document.getElementById("cancelDelete").onclick = () => {
        modal.style.display = "none"; // Close modal without deleting
    };
}

// Delete News Function
async function deleteNews(newsId) {
    try {
        const response = await fetch(`/news/hr/delete/${newsId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.ok) {
            showModal("News Deleted", "success");
            fetchHRNews();
        } else {
            showModal("Failed to Delete News", "failure");
        }
    } catch (error) {
        console.error("Error deleting news:", error);
        showModal("An error occurred while deleting news.", "failure");
    }
}

/***************************************************************************************************************/

// Show Success/Error Messages in a Modal
function showModal(message, type = 'success') {
    const modal = document.getElementById('raiseModal');
    const modalMessage = document.getElementById('raise-modal-message');

    modalMessage.textContent = message;
    
    // Reset modal class and apply appropriate styling
    modal.className = 'modal'; // Reset any existing classes
    if (type === 'success') {
        modal.style.backgroundColor = '#28a745'; // Green for success
    } else {
        modal.style.backgroundColor = '#dc3545'; // Red for failure
    }

    modal.style.display = 'block';

    // Auto-fade and remove after 3 seconds
    setTimeout(() => {
        modal.classList.add('fade-out');
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade-out'); // Reset for next use
        }, 500);
    }, 3000);
}