from fastapi import  Form , APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse 
from bson import ObjectId 
from app.auth import get_current_user
from datetime import datetime
from uuid import uuid4
from app.models import News , Comment
from app.config import news_collection
from typing import Optional 
import uuid



router = APIRouter()

# OAuth2PasswordBearer is used to extract JWT token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



################################################################################################################
# Add news article
@router.post("/add")
async def create_news(title: str = Form(...), content: str = Form(...), author: str = Form(...)):
    news_id = f"NEWS{uuid.uuid4().hex[:6].upper()}"
    
    new_news = {
        "news_id": news_id,
        "title": title,
        "content": content,
        "date": datetime.utcnow(),
        "author": author,
        "comments": []
    }
    
    news_collection.insert_one(new_news)
    return {"message": "News created successfully.", "news_id": news_id}


################################################################################################################

# Get all news articles

@router.get("/get")
def get_all_news():
    news_list = list(news_collection.find({}))
    for news in news_list:
        news["_id"] = str(news["_id"])
    return news_list



################################################################################################################

# Get a single news article by ID
@router.get("/get/{news_id}")
def get_news(news_id: str):
    # Query using custom news_id instead of MongoDB's ObjectId
    news = news_collection.find_one({"news_id": news_id})  

    if not news:
        raise HTTPException(status_code=404, detail="News article not found")

    news["_id"] = str(news["_id"])  # Convert ObjectId to string (if it exists)
    return news


################################################################################################################

# Update a news article

@router.put("/update/{news_id}")
def update_news(news_id: str, title: str = Form(...), content: str = Form(...), author: str = Form(...)):
    updated_data = {
        "title": title,
        "content": content,
        "author": author,
        "date": f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} (edited)"
    }

    update_result = news_collection.update_one(
        {"news_id": news_id},
        {"$set": updated_data}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="News article not found or no changes made")

    return {"message": "News updated successfully"}


################################################################################################################

# Delete a news article

@router.delete("/delete/{news_id}")
def delete_news(news_id: str):
    delete_result = news_collection.delete_one({"news_id": news_id})  # Use "news_id" instead of "_id"
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="News article not found")
    
    return {"message": "News deleted successfully"}


################################################################################################################

# Endpoint to add a comment to a news article

@router.put("/comment/{news_id}")
async def add_comment(
    news_id: str,
    comment_content: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    news_item = news_collection.find_one({"news_id": news_id})
    if not news_item:
        raise HTTPException(status_code=404, detail="News article not found.")

    comment = {
        "id": str(uuid.uuid4()),  # Generate unique ID for comment
        "username": current_user["username"],
        "content": comment_content,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

    update_result = news_collection.update_one(
        {"news_id": news_id},
        {"$push": {"comments": comment}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add comment.")

    return {"message": "Comment added successfully."}


################################################################################################################
#Delete Specific Comments

@router.delete("/comment/{news_id}/delete/{comment_id}")
async def delete_comment(news_id: str, comment_id: str):
    # Check if the news article exists
    news_item = news_collection.find_one({"news_id": news_id})
    if not news_item:
        raise HTTPException(status_code=404, detail="News article not found.")

    # Remove the specific comment by its comment_id
    update_result = news_collection.update_one(
        {"news_id": news_id},
        {"$pull": {"comments": {"id": comment_id}}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found or already deleted.")

    return {"message": "Comment deleted successfully."}


################################################################################################################
# Endpoint to retrieve news with comments

@router.get("/get/{news_id}")
async def get_news(news_id: str):
    # Query by the custom 'news_id' instead of ObjectId
    news = news_collection.find_one({"news_id": news_id})

    if not news:
        raise HTTPException(status_code=404, detail="News article not found.")

    # Convert ObjectId to string for JSON response
    news["_id"] = str(news["_id"])
    
    return news





##################################################################################################################
############################################ HR EXCLUSIVE #######################################################
##################################################################################################################


##################################################################################################################

# Creating News 

@router.post("/hr/create")
async def add_news_article(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Depends(get_current_user),
    current_user: dict = Depends(get_current_user)
):
    # Ensure only HR can add news
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Create a new news article
    news_article = {
        "news_id": str(uuid4()),
        "title": title,
        "content": content,
        "author": author["username"],
        "published_at": datetime.utcnow(),
        "last_updated": None,
        "comments": []  # Empty list for comments
    }

    news_collection.insert_one(news_article)

    return JSONResponse(content={"message": "News article created successfully"}, status_code=201)


##################################################################################################################

# Editing Existing News 

@router.put("/hr/edit/{news_id}")
async def edit_news_article(
    news_id: str,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    # Ensure only HR can edit news
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the news article
    news_article = news_collection.find_one({"news_id": news_id})
    if not news_article:
        raise HTTPException(status_code=404, detail="News article not found")

    # Update fields
    update_data = {}
    if title:
        update_data["title"] = title
    if content:
        update_data["content"] = content
    update_data["last_updated"] = datetime.utcnow()

    # Update the article
    news_collection.update_one({"news_id": news_id}, {"$set": update_data})

    return JSONResponse(content={"message": "News article updated successfully"}, status_code=200)

##################################################################################################################
# Deleting News

@router.delete("/hr/delete/{news_id}")
async def delete_news_article(
    news_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Ensure only HR can delete news
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the news article
    news_article = news_collection.find_one({"news_id": news_id})
    if not news_article:
        raise HTTPException(status_code=404, detail="News article not found")

    # Delete the news article
    news_collection.delete_one({"news_id": news_id})

    return JSONResponse(content={"message": "News article deleted successfully"}, status_code=200)



##################################################################################################################

# Deleting comments on news 


@router.delete("/hr/delete/{news_id}/comment/{comment_id}")
async def delete_comment(
    news_id: str,
    comment_id: str,  # This will now match `id` in the comment object
    current_user: dict = Depends(get_current_user)
):
    # Ensure only HR can delete comments
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the news article
    news_article = news_collection.find_one({"news_id": news_id})
    if not news_article:
        raise HTTPException(status_code=404, detail="News article not found")

    # Check if comments exist
    if "comments" not in news_article or not isinstance(news_article["comments"], list):
        raise HTTPException(status_code=400, detail="No comments found on this article.")

    # Remove the comment with matching `id` instead of `comment_id`
    updated_comments = [
        comment for comment in news_article["comments"] if comment.get("id") != comment_id
    ]

    # Check if a comment was removed
    if len(updated_comments) == len(news_article["comments"]):
        raise HTTPException(status_code=404, detail="Comment not found.")

    # Update the news article by removing the comment
    news_collection.update_one({"news_id": news_id}, {"$set": {"comments": updated_comments}})

    return JSONResponse(content={"message": "Comment deleted successfully"}, status_code=200)


##################################################################################################################