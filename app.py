from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from hybrid_search import get_search_results

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        search_results = get_search_results(query)
        images = []
        for elem in search_results:
            images.append(elem[1])
        return render_template("search_results.html", images=images)
    else:
        return render_template('search_form.html')


if __name__ == '__main__':
    app.run()
