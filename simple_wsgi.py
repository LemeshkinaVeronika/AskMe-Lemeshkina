def application(environ, start_response):
    
    get_params = {}
    query_string = environ.get('QUERY_STRING', '')
    if query_string:
        get_params = dict(pair.split('=') for pair in query_string.split('&') if '=' in pair)
    
    post_params = {}
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    
    if request_body_size > 0:
        request_body = environ['wsgi.input'].read(request_body_size)
        post_params = dict(pair.split('=') for pair in request_body.decode().split('&') if '=' in pair)
    
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    
    response_body = "GET parameters:\n"
    for key, value in get_params.items():
        response_body += f"{key}: {value}\n"
    
    response_body += "\nPOST parameters:\n"
    for key, value in post_params.items():
        response_body += f"{key}: {value}\n"
    
    start_response(status, headers)
    return [response_body.encode('utf-8')]