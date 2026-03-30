from flask import Blueprint

oauth_routes = Blueprint('oauth', __name__)

@oauth_routes.route("/oauth_callback", methods=["GET"])
def oauth_callback():
    return """<head>
   <script src="https://yastatic.net/s3/passport-sdk/autofill/v1/sdk-suggest-token-with-polyfills-latest.js"></script>
</head><body>
<script>
YaSendSuggestToken(
   'http://localhost:5000', 
   {
      "flag": true
   }
)
</script>
</body>"""