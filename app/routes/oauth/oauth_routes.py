from flask import Blueprint
from flask import request
oauth_routes = Blueprint('oauth', __name__)

@oauth_routes.route("/oauth_callback", methods=["GET"])
def oauth_callback():
    print(request.data, "\nHI\n", dict(request.args))
    return """<head>
   <script src="https://yastatic.net/s3/passport-sdk/autofill/v1/sdk-suggest-token-with-polyfills-latest.js"></script>
</head><body>
<script>
YaSendSuggestToken(
   'https://biplabproject.ru', 
   
   {
      "flag": true,
      "test": 10
   }
)
</script>
<p>Please, wait</p>
</body>"""


@oauth_routes.route("/oauth_getter", methods=["POST"])
def oauth_getter():
    print(request.data,"\nHI\n",request.args)
