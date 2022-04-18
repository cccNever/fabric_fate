from app import create_app

app = create_app()


@app.route('/test')
def test():
    return 'test'


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=88, debug=False )
