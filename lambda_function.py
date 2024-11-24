import requests
import markdown
import boto3

# Set the S3 client
s3_client = boto3.client('s3')

# Step 1: Set your API Key from NewsAPI
API_KEY = 'd6f098e271eb4eb59c2b1f6812093639'

# Step 2: Define the endpoint and parameters
url = "https://newsapi.org/v2/top-headlines"
params = {
    'apiKey': API_KEY,
    'country': 'us',
    'category': 'technology',
    'pageSize': 5
}

# Fetch and save news articles
def lambda_handler(event, context):
    # S3 Bucket and file keys
    s3_bucket_name = 'output-files-for-news-publication'  # Replace with your S3 bucket name
    markdown_file_key = 'weekly_tech_blog.md'
    html_file_key = 'weekly_tech_blog.html'

    # Step 3: Send the request to the NewsAPI endpoint
    response = requests.get(url, params=params)

    # Step 4: Check for successful response
    if response.status_code != 200:
        return {"status": "error", "message": f"Failed to fetch news: {response.status_code}"}

    news_data = response.json()
    articles = news_data.get('articles', [])
    if not articles:
        return {"status": "error", "message": "No articles found."}

    # Initialize blog content
    blog_title = "This Week in Tech: Top Headlines"
    blog_introduction = "Here are the latest developments in technology. Stay informed!"
    blog_content = [f"# {blog_title}\n\n", f"## Introduction\n{blog_introduction}\n\n", "## Articles:\n"]

    seen_titles = set()  # Track duplicate titles
    for article in articles:
        title = article.get('title')
        description = article.get('description')
        article_url = article.get('url')

        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        # Add article title, description, and URL
        blog_content.append(f"### {title}\n")
        blog_content.append(f"**[Read more]({article_url})**\n")
        blog_content.append(f"**Description**: {description or 'No description available.'}\n\n")

    blog_conclusion = "Stay tuned for more updates in the tech world!"
    blog_content.append(f"## Conclusion\n{blog_conclusion}\n")

    # Save to Markdown content
    markdown_content = "\n".join(blog_content)

    # Upload the Markdown content to S3
    s3_client.put_object(
        Bucket=s3_bucket_name,
        Key=markdown_file_key,
        Body=markdown_content,
        ContentType='text/markdown',
        ACL='public-read'  # Optional, depending on your access policy
    )

    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content)

    # Upload the HTML content to S3
    s3_client.put_object(
        Bucket=s3_bucket_name,
        Key=html_file_key,
        Body=html_content,
        ContentType='text/html',
        ACL='public-read'  # Optional, depending on your access policy
    )

    return {
        "status": "success",
        "markdown_url": f"https://{s3_bucket_name}.s3.amazonaws.com/{markdown_file_key}",
        "html_url": f"https://{s3_bucket_name}.s3.amazonaws.com/{html_file_key}"
    }
