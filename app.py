import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from newsapi import NewsApiClient

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = 'anurag1843panda@gmail.com'


mail = Mail(app)

def get_sources_and_domains():
    all_sources = newsapi.get_sources()['sources']
    sources = []
    domains = []
    for source in all_sources:
        if isinstance(source['id'], int):
            id = source['id']
            domain = source['url'].replace("http://", "").replace("https://", "").replace("www.", "")
            slash_index = domain.find('/')
            if slash_index != -1:
                domain = domain[:slash_index]
            sources.append(id)
            domains.append(domain)
            print(source)
    sources_str = ", ".join(sources)
    domains_str = ", ".join(domains)
    return sources_str, domains_str

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if keyword:
            page = request.args.get('page', 1, type=int)
            sources, domains = get_sources_and_domains()
            try:
                related_news = newsapi.get_everything(q=keyword,
                                                       sources=sources,
                                                       domains=domains,
                                                       language='en',
                                                       sort_by='relevancy',
                                                       page=page)
                if 'totalResults' in related_news:
                    total_results = min(related_news['totalResults'], 100)
                    all_articles = related_news['articles']
                    return render_template("index.html", all_articles=all_articles, keyword=keyword, total_results=total_results, page=page)
                else:
                    flash("No results found.")
            except Exception as e:
                flash(f"An error occurred: {str(e)}. Please try again later.")
        else:
            flash("Please enter a keyword to search.")
        return redirect(url_for('index'))

    top_headlines = newsapi.get_top_headlines(country="in", language="en")
    if 'totalResults' in top_headlines:
        total_results = min(top_headlines['totalResults'], 100)
        all_headlines = top_headlines['articles']
        return render_template("index.html", all_headlines=all_headlines, total_results=total_results)
    return render_template("index.html")

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        send_email(name, email, message)
        print(f"Name: {name}, Email: {email}, Message: {message}")

        # Flash a success message
        flash("Your message has been sent successfully!")

        # Redirect to the index page
        return redirect(url_for('index'))

    # Render the contact form template
    return render_template("contact.html")


def send_email(name, email, message):
    msg = Message('Contact Form Submission', sender=os.getenv("MAIL_USERNAME"), recipients=[os.getenv("RECIPIENT_EMAIL")])
    msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    mail.send(msg)
    
    
@app.route("/about")
def about():
    return render_template("aboutus.html")
    
    
if __name__ == "__main__":
    app.run(debug=True)