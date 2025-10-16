def httpStatus(status):
    match status:
        case 200:
            return "OK"
        case 201 | 202:
            return "Created"
        case 204:
            return "No content"
        case 301 | 302:
            return "Moved permanently"
        case 304:
            return "Not modified"
        case 307 | 308:
            return "Temporary redirect"
        case 400:
            return "Bad request"
        case 404:
            return "Not found"
        case 418:
            return "I'm a teapot"
        case 500:
            return "Internal server error"
        case 502:
            return "Bad gateway"
        case 503:
            return "Service unavailable"
        case _:
            return "Something's wrong with the internet"
        
print(httpStatus(200))
print(httpStatus(418))
